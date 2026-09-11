# main_upright.py
# Simulazione Cart-Pole UPRIGHT: controllo LQR
# Target: (x, dx, theta, dth) = (0, 0, pi, 0) — equilibrio alto instabile
#
# Stesso impianto fisico del Convey-Crane (model/cart_pole.xml),
# stesso stile di main.py, ma con linearizzazione e controllore
# diversi (vedi controllers/lqr_upright.py).

import mujoco
import mujoco.viewer
import numpy as np
import matplotlib.pyplot as plt
import time

from controllers.lqr_upright import design_lqr, lqr_control, theta_to_phi
from utils.viz_helpers import add_target_marker

# ── Setup modello ──────────────────────────────────────────────────
model = mujoco.MjModel.from_xml_path("model/cart_pole.xml")
data  = mujoco.MjData(model)
dt    = model.opt.timestep

# ── Guadagno LQR (calcolato una sola volta) ────────────────────────
K, A, B, P = design_lqr()
print(f"Guadagno K (upright) = {K}")

# ── Stato iniziale: vicino all'equilibrio ALTO ─────────────────────
PHI0_DEG = 15.0   # scostamento iniziale dall'equilibrio alto, in gradi
data.qpos[0] = 0.0                          # x0 = 0
data.qpos[1] = np.pi + np.deg2rad(PHI0_DEG) # theta0 = pi + 15°
data.qvel[:] = 0.0

F_MAX = 50.0   # deve combaciare con ctrlrange nell'XML

# ── Logging ────────────────────────────────────────────────────────
log = {'t': [], 'x': [], 'phi': [], 'dx': [], 'dth': [], 'F': []}


# ── Loop di simulazione ────────────────────────────────────────────
with mujoco.viewer.launch_passive(model, data) as viewer:
    viewer.cam.azimuth   = 90
    viewer.cam.elevation = -15
    viewer.cam.distance  = 6.0
    viewer.cam.lookat[:] = [0.0, 0, 0.5]   # pendolo sta in alto: lookat più su

    t = 0.0
    T_max = 12.0

    add_target_marker(viewer, x_target=0.0, theta_target=np.pi)

    while viewer.is_running() and t < T_max:
        x     = data.qpos[0]
        theta = data.qpos[1]
        dx    = data.qvel[0]
        dth   = data.qvel[1]

        F = lqr_control([x, dx, theta, dth], K)
        F = np.clip(F, -F_MAX, F_MAX)
        data.ctrl[0] = F

        mujoco.mj_step(model, data)
        viewer.sync()

        phi = theta_to_phi(theta)
        log['t'].append(t)
        log['x'].append(x)
        log['phi'].append(phi)
        log['dx'].append(dx)
        log['dth'].append(dth)
        log['F'].append(F)

        t += dt
        time.sleep(dt)

# ── Plot risultati ─────────────────────────────────────────────────
t_arr = np.array(log['t'])
fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)

axes[0].plot(t_arr, log['x'], color='steelblue', label='x (carrello)')
axes[0].axhline(0, color='k', linestyle=':', alpha=0.4)
axes[0].set_ylabel('Posizione [m]')
axes[0].legend(); axes[0].grid(True)

axes[1].plot(t_arr, np.degrees(log['phi']), color='coral',
             label='φ = θ - π (deviazione da verticale alto)')
axes[1].axhline(0, color='k', linestyle=':', alpha=0.4)
axes[1].set_ylabel('Angolo [°]')
axes[1].legend(); axes[1].grid(True)

axes[2].plot(t_arr, log['F'], color='purple', label='F [N]')
axes[2].axhline( F_MAX, color='r', linestyle=':', alpha=0.5, label='saturazione')
axes[2].axhline(-F_MAX, color='r', linestyle=':', alpha=0.5)
axes[2].set_ylabel('Forza [N]')
axes[2].set_xlabel('Tempo [s]')
axes[2].legend(); axes[2].grid(True)

plt.suptitle(f'Cart-Pole Upright — Controllo LQR (φ₀={PHI0_DEG}°)', fontsize=14)
plt.tight_layout()
plt.savefig('risultati_upright.png', dpi=150)
plt.show()
print("Plot salvato in risultati_upright.png")