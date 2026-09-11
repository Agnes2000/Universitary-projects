# main_lqr.py
# Simulazione Convey-Crane: controllo LQR (equilibrio BASSO)
# Target: (x, dx, th, dth) = (0, 0, 0, 0) — equilibrio basso stabile
#
# Stesso impianto fisico e stessa condizione iniziale di main.py
# (passivity), per confronto diretto LQR vs passivity-based.

import mujoco
import mujoco.viewer
import numpy as np
import matplotlib.pyplot as plt
import time

from controllers.lqr import design_lqr, lqr_control
from utils.params import total_energy
from utils.viz_helpers import add_target_marker

# ── Setup modello ──────────────────────────────────────────────────
model = mujoco.MjModel.from_xml_path("model/cart_pole.xml")
data  = mujoco.MjData(model)
dt    = model.opt.timestep

# ── Guadagno LQR (calcolato una sola volta) ────────────────────────
K, A, B, P = design_lqr()
print(f"Guadagno K (basso) = {K}")

# ── Stato iniziale: stesso del Test 1 del paper (vedi main.py) ─────
data.qpos[0] = -5.0          # x0 = -5
data.qpos[1] = -np.pi/4      # th0 = -45°
data.qvel[:] = 0.0

F_MAX = 50.0   # deve combaciare con ctrlrange nell'XML

# ── Logging ────────────────────────────────────────────────────────
log = {'t': [], 'x': [], 'th': [], 'dx': [], 'dth': [], 'F': [], 'E': []}

# ── Loop di simulazione ────────────────────────────────────────────
with mujoco.viewer.launch_passive(model, data) as viewer:
    viewer.cam.azimuth   = 90
    viewer.cam.elevation = -15
    viewer.cam.distance  = 12.0
    viewer.cam.lookat[:] = [-2.5, 0, -0.5]

    t = 0.0
    T_max = 12.0

    add_target_marker(viewer, x_target=0.0, theta_target=0.0)

    while viewer.is_running() and t < T_max:
        x   = data.qpos[0]
        th  = data.qpos[1]
        dx  = data.qvel[0]
        dth = data.qvel[1]

        F = lqr_control([x, dx, th, dth], K)
        F = np.clip(F, -F_MAX, F_MAX)
        data.ctrl[0] = F

        mujoco.mj_step(model, data)
        viewer.sync()

        E = total_energy(th, dth)
        log['t'].append(t)
        log['x'].append(x)
        log['th'].append(th)
        log['dx'].append(dx)
        log['dth'].append(dth)
        log['F'].append(F)
        log['E'].append(E)

        t += dt
        time.sleep(dt)

# ── Plot risultati ─────────────────────────────────────────────────
t_arr = np.array(log['t'])
fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)

axes[0].plot(t_arr, log['x'], color='steelblue', label='x (carrello)')
axes[0].axhline(0, color='k', linestyle=':', alpha=0.4)
axes[0].set_ylabel('Posizione [m]')
axes[0].legend(); axes[0].grid(True)

axes[1].plot(t_arr, np.degrees(log['th']), color='coral', label='θ (pendolo)')
axes[1].axhline(0, color='k', linestyle=':', alpha=0.4)
axes[1].set_ylabel('Angolo [°]')
axes[1].legend(); axes[1].grid(True)

axes[2].plot(t_arr, log['F'], color='purple', label='F [N]')
axes[2].axhline( F_MAX, color='r', linestyle=':', alpha=0.5, label='saturazione')
axes[2].axhline(-F_MAX, color='r', linestyle=':', alpha=0.5)
axes[2].set_ylabel('Forza [N]')
axes[2].legend(); axes[2].grid(True)

axes[3].plot(t_arr, log['E'], color='darkorange', label='E(t) pendolo')
axes[3].axhline(0, color='green', linestyle='--', label='E*=0')
axes[3].set_ylabel('Energia [J]')
axes[3].set_xlabel('Tempo [s]')
axes[3].legend(); axes[3].grid(True)

plt.suptitle('Convey-Crane — Controllo LQR (equilibrio basso)', fontsize=14)
plt.tight_layout()
plt.savefig('risultati_lqr.png', dpi=150)
plt.show()
print("Plot salvato in risultati_lqr.png")