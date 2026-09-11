# Simulazione completa Reaction Wheel Pendulum: swingup + balance FL
#
# CONVENZIONE: q1=0 -> pendolo in su (goal), q1=π -> in giù (partenza)

import mujoco
import mujoco.viewer
import numpy as np
import matplotlib.pyplot as plt
import time

from controllers.balance_fl import balance_control
from controllers.swingup    import swingup_control
from controllers.supervisor import should_switch_to_balance, should_switch_to_swingup
from utils.params import total_energy

# ── Setup modello ──────────────────────────────────────────────────
model = mujoco.MjModel.from_xml_path("model/rwp.xml")
data  = mujoco.MjData(model)
dt    = model.opt.timestep

# ── Stato iniziale: pendolo in basso ───────────────────────────────
data.qpos[0] = np.pi
data.qpos[1] = 0.0
data.qvel[0] = 0.05    # piccola perturbazione per innescare il moto
data.qvel[1] = 0.0

TAU_MAX = 3.0   # deve combaciare con ctrlrange nell'XML
mode = 0        # 0=swingup, 1=balance

log = {'t': [], 'q1': [], 'q2': [], 'dq1': [], 'dq2': [],
       'tau': [], 'E': [], 'mode': []}

with mujoco.viewer.launch_passive(model, data) as viewer:
    # Camera fissa, calcolata sulla geometria del tuo RWP
    viewer.cam.lookat[:] = [0, 0, 0.3]   # punto centrale: metà altezza pendolo+disco esteso
    viewer.cam.distance = 1.5            # ~2-3x la lunghezza totale del braccio
    viewer.cam.azimuth = 90              # ruota per inquadrare frontalmente
    viewer.cam.elevation = -15     
    
    t = 0.0
    T_max = 65.0

    mode = 0        # 0=swingup, 1=balance
    switch_time = None   # <-- AGGIUNGI QUESTA RIGA prima del while
    switch_count = 0   # <-- AGGIUNGI

    min_balance_duration = 0.5
    time_in_balance = 0.0

    while viewer.is_running() and t < T_max:
        q1, q2   = data.qpos[0], data.qpos[1]
        dq1, dq2 = data.qvel[0], data.qvel[1]

        if mode == 0 and should_switch_to_balance(q1, q2, dq1, dq2):
            mode = 1
            switch_time = t   # <-- AGGIUNGI QUESTA RIGA
            switch_count += 1   # <-- AGGIUNGI
            print(f"[t={t:.2f}s] SWITCH -> balance FL")
        # dentro il while, nel ramo elif:
        elif mode == 1 and should_switch_to_swingup(q1, q2, dq1, dq2) and time_in_balance > min_balance_duration:
            mode = 0
            print(f"[t={t:.2f}s] SWITCH -> swingup")

        if mode == 1:
            time_in_balance += dt
        else:
            time_in_balance = 0.0

        if mode == 0:
            tau = swingup_control(q1, q2, dq1, dq2, ke=1500.0, kv=1.0)
        else:
            tau = balance_control(q1, q2, dq1, dq2, k1=100.0, k2=50.0, k3=10.0)

        tau = np.clip(tau, -TAU_MAX, TAU_MAX)
        data.ctrl[0] = tau

         # Debug ristretto: stampa solo 1 riga ogni 200 step (0.2s), sempre
        if int(t/dt) % 200 == 0:
            q1n_deg = np.degrees(np.arctan2(np.sin(q1), np.cos(q1)))
            print(f"  t={t:6.2f}  mode={mode}  q1n={q1n_deg:+7.2f}  dq1={dq1:+.4f}  dq2={dq2:+.4f}  tau={tau:+.4f}")

        mujoco.mj_step(model, data)
        viewer.sync()

        E = total_energy(q1, dq1)
        log['t'].append(t)
        log['q1'].append(q1)
        log['q2'].append(q2)
        log['dq1'].append(dq1)
        log['dq2'].append(dq2)
        log['tau'].append(tau)
        log['E'].append(E)
        log['mode'].append(mode)

        t += dt
        time.sleep(dt)

# ── Plot ────────────────────────────────────────────────────────────
t_arr = np.array(log['t'])
fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)

t_switch = next((log['t'][i] for i, m in enumerate(log['mode']) if m == 1), None)
def add_switch_line(ax):
    if t_switch:
        ax.axvline(t_switch, color='green', linestyle='--', alpha=0.7, label='Switch->Balance')

axes[0].plot(t_arr, np.degrees(log['q1']), color='steelblue', label='q1 (pendolo)')
axes[0].axhline(0, color='k', linestyle=':', alpha=0.4, label='goal q1=0')
add_switch_line(axes[0]); axes[0].set_ylabel('Angolo [°]'); axes[0].legend(); axes[0].grid(True)

axes[1].plot(t_arr, log['dq2'], color='coral', label='dq2 (disco)')
add_switch_line(axes[1]); axes[1].set_ylabel('Vel. disco [rad/s]'); axes[1].legend(); axes[1].grid(True)

axes[2].plot(t_arr, log['tau'], color='purple', label='τ [Nm]')
add_switch_line(axes[2])
axes[2].axhline( TAU_MAX, color='r', linestyle=':', alpha=0.5)
axes[2].axhline(-TAU_MAX, color='r', linestyle=':', alpha=0.5)
axes[2].set_ylabel('Coppia [Nm]'); axes[2].legend(); axes[2].grid(True)

axes[3].plot(t_arr, log['E'], color='darkorange', label='E(t)')
axes[3].axhline(0, color='green', linestyle='--', label='E*=0')
add_switch_line(axes[3])
axes[3].set_ylabel('Energia [J]'); axes[3].set_xlabel('Tempo [s]'); axes[3].legend(); axes[3].grid(True)

plt.suptitle('Reaction Wheel Pendulum — Swingup + Balance FL', fontsize=14)
plt.tight_layout()
plt.savefig('risultati.png', dpi=150)
plt.show()
print("Plot salvato in risultati.png")