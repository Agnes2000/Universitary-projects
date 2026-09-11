"""
Terzo caso del progetto: swing-up del Convey-Crane con trajectory
optimization (DDP/iLQR), poi stabilizzazione con l'LQR upright gia'
esistente (controllers/lqr_upright.py).

STORIA DI PROGETTAZIONE (importante per l'orale):
Il primo tentativo era: usare i guadagni di feedback K_k prodotti dal
backward pass del DDP per TUTTA la traiettoria pianificata (350 step),
poi passare a lqr_upright solo alla fine. Risultato: divergenza
catastrofica (theta arrivava a superare i 600 gradi, giri completi).

Causa: vicino all'equilibrio alto instabile i guadagni K_k del DDP
diventano enormi (norma fino a ~136, contro ~1-5 nella parte iniziale
della traiettoria) — cosa fisicamente sensata (serve piu' guadagno vicino
a un equilibrio instabile), ma quando l'errore di tracking (dovuto al
naturale model-mismatch: il DDP pianifica su un modello Euler
approssimato, MuJoCo integra con RK4) incontra un guadagno enorme, la
correzione richiesta supera i limiti dell'attuatore (+-50N), F satura,
il controllore non riesce piu' a correggere, l'errore cresce ancora di
piu', il DDP "chiede" una correzione ancora piu' grande (ma inutile,
gia' saturo) -> collasso a catena (windup).

Soluzione adottata: NON usare mai i guadagni K_k del DDP nella regione
mal condizionata vicino al target. Si passa il testimone a lqr_upright
(guadagni fissi, gia' verificato, bacino di attrazione noto ~60-70 gradi
da progetto) non appena lo stato entra nel suo bacino di attrazione,
invece di aspettare la fine dei 350 step pianificati. Verificato: niente
piu' saturazione, convergenza pulita.
"""

import mujoco
import mujoco.viewer
import numpy as np
import matplotlib.pyplot as plt
import time

from controllers import trajopt_swingup as ts
from controllers import ddp
from controllers.lqr_upright import design_lqr, lqr_control, theta_to_phi
from utils.viz_helpers import add_target_marker

# ============================================================
# NOTA SULLE CONVENZIONI DI STATO — attenzione, sono diverse:
#   trajopt_swingup.py / ddp.py usano l'ordine  [x, theta, dx, dtheta]
#   lqr_control (lqr_upright.py) usa l'ordine   [x, dx, theta, dth]
# Le funzioni sotto servono solo a non confondere i due ordini quando
# si passa da un controllore all'altro.
# ============================================================

def mujoco_state_ddp_order(data):
    """Stato letto da MuJoCo nell'ordine usato dal DDP: [x, theta, dx, dtheta]."""
    return np.array([data.qpos[0], data.qpos[1], data.qvel[0], data.qvel[1]])


# ── Configurazione ──────────────────────────────────────────
FEEDBACK_ENABLED = True     # True: u = ubar + K_k*(x-xbar) durante lo swing-up
                             # False: solo feedforward ubar (per il confronto)
N_PLAN = 350                 # step della traiettoria DDP (= test_ddp_swingup.py)
SWITCH_THRESHOLD_DEG = 60.0  # soglia |theta-pi| per passare a lqr_upright
                             # (bacino di attrazione documentato di lqr_upright)
F_MAX = 50.0

# Criterio di convergenza per terminare la stabilizzazione (invece di un
# tempo fisso arbitrario): la dinamica di lqr_upright su x e' lenta (il
# guadagno su x e' piccolo, -1), la convergenza completa richiede ~20s
# dopo lo switch — molto piu' dei 5s fissi usati inizialmente, per questo
# la simulazione si fermava troppo presto. Ora si ferma da sola quando lo
# stato e' davvero vicino al target, non prima.
CONV_X_TOL = 0.01          # [m]
CONV_PHI_TOL_DEG = 0.5     # [deg]
CONV_VEL_TOL = 0.01        # [m/s] e [rad/s]
CONV_CONFIRM_TIME = 1.0    # [s] quanto deve restare dentro tolleranza prima di fermarsi
T_MAX_ABSOLUTE = 40.0       # [s] tetto di sicurezza, non dovrebbe mai servire


def compute_ddp_trajectory():
    print("Calcolo offline della traiettoria DDP (swing-up)...")
    x0 = np.array([0.0, 0.0, 0.0, 0.0])
    U_init = np.zeros((N_PLAN, 1))
    X_traj, U_traj, k_list, K_list, history = ddp.solve_ddp(
        x0, U_init,
        ts.dynamics_step, ts.dynamics_jacobians,
        ts.running_cost, ts.running_cost_grad, ts.running_cost_hess,
        ts.terminal_cost, ts.terminal_cost_grad, ts.terminal_cost_hess,
        ts.DT, max_iters=150, tol=1e-6, verbose=False
    )
    print(f"DDP: costo finale={history[-1]:.3f}, "
          f"theta_finale={np.degrees(X_traj[-1][1]):.2f} deg, "
          f"iterazioni={len(history)}")
    return X_traj, U_traj, K_list


def main():
    X_traj, U_traj, K_list = compute_ddp_trajectory()

    model = mujoco.MjModel.from_xml_path("model/cart_pole.xml")
    data = mujoco.MjData(model)
    sim_dt = model.opt.timestep            # 0.001, MuJoCo
    plan_dt = ts.DT                        # 0.02, DDP
    substeps = round(plan_dt / sim_dt)     # 20

    K_lqr_up, A_up, B_up, P_up = design_lqr()
    print(f"Guadagno LQR upright = {K_lqr_up}")

    # Stato iniziale: equilibrio basso, come pianificato dal DDP
    data.qpos[0] = 0.0
    data.qpos[1] = 0.0
    data.qvel[:] = 0.0

    switch_threshold = np.deg2rad(SWITCH_THRESHOLD_DEG)
    switched = False
    switch_time = None
    k_plan = 0
    step_count = 0

    T_max = T_MAX_ABSOLUTE  # tetto di sicurezza; normalmente si ferma prima per convergenza
    converged_since = None   # istante da cui lo stato e' entrato in tolleranza

    log = {'t': [], 'x': [], 'theta': [], 'F': [], 'phase': []}
    t = 0.0

    with mujoco.viewer.launch_passive(model, data) as viewer:
        viewer.cam.azimuth = 90
        viewer.cam.elevation = -15
        viewer.cam.distance = 6.0
        viewer.cam.lookat[:] = [0.0, 0, 1.5]

        add_target_marker(viewer, x_target=0.0, theta_target=np.pi)

        while viewer.is_running() and t < T_max:
            x = data.qpos[0]
            theta = data.qpos[1]
            dx = data.qvel[0]
            dth = data.qvel[1]
            phi = theta_to_phi(theta)

            # Switch (irreversibile) a lqr_upright: appena nel bacino di
            # attrazione, o come fallback se la finestra DDP e' terminata
            if not switched and (abs(phi) < switch_threshold or k_plan >= N_PLAN):
                switched = True
                switch_time = t
                print(f"Switch a lqr_upright a t={t:.2f}s "
                      f"(phi={np.degrees(phi):.1f} deg, k_plan={k_plan})")

            if switched:
                F = lqr_control([x, dx, theta, dth], K_lqr_up)
                phase = 'lqr_upright'
            else:
                x_bar = X_traj[k_plan]
                u_bar = U_traj[k_plan]
                Kk = K_list[k_plan]
                x_real_ddp = mujoco_state_ddp_order(data)
                dx_state = x_real_ddp - x_bar
                if FEEDBACK_ENABLED:
                    F = u_bar[0] + (Kk @ dx_state)[0]
                else:
                    F = u_bar[0]
                phase = 'trajopt'

            F = float(np.clip(F, -F_MAX, F_MAX))
            data.ctrl[0] = F

            mujoco.mj_step(model, data)
            viewer.sync()

            log['t'].append(t)
            log['x'].append(x)
            log['theta'].append(theta)
            log['F'].append(F)
            log['phase'].append(phase)

            step_count += 1
            if not switched and step_count % substeps == 0:
                k_plan += 1

            # Criterio di arresto per convergenza (solo dopo lo switch):
            # se lo stato resta dentro tolleranza per CONV_CONFIRM_TIME
            # secondi consecutivi, la simulazione termina da sola.
            if switched:
                phi_deg_now = abs(np.degrees(theta_to_phi(data.qpos[1])))
                in_tol = (abs(data.qpos[0]) < CONV_X_TOL and
                          phi_deg_now < CONV_PHI_TOL_DEG and
                          abs(data.qvel[0]) < CONV_VEL_TOL and
                          abs(data.qvel[1]) < CONV_VEL_TOL)
                if in_tol:
                    if converged_since is None:
                        converged_since = t
                    elif t - converged_since >= CONV_CONFIRM_TIME:
                        print(f"Convergenza confermata a t={t:.2f}s "
                              f"(x={data.qpos[0]:.4f}, phi={phi_deg_now:.2f}deg)")
                        t += sim_dt
                        break
                else:
                    converged_since = None

            t += sim_dt
            time.sleep(sim_dt)

    # ── Plot risultati ──────────────────────────────────────
    t_arr = np.array(log['t'])
    theta_arr = np.degrees(np.array(log['theta']))
    x_arr = np.array(log['x'])
    F_arr = np.array(log['F'])

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)

    axes[0].plot(t_arr, x_arr, color='steelblue')
    if switch_time is not None:
        axes[0].axvline(switch_time, color='gray', linestyle='--', alpha=0.6,
                         label='switch a lqr_upright')
    axes[0].set_ylabel('x carrello [m]')
    axes[0].legend(); axes[0].grid(True)

    axes[1].plot(t_arr, theta_arr, color='coral')
    axes[1].axhline(180, color='g', linestyle=':', alpha=0.6, label='target (180°)')
    if switch_time is not None:
        axes[1].axvline(switch_time, color='gray', linestyle='--', alpha=0.6)
    axes[1].set_ylabel('theta [deg]')
    axes[1].legend(); axes[1].grid(True)

    axes[2].plot(t_arr, F_arr, color='purple')
    axes[2].axhline(F_MAX, color='r', linestyle=':', alpha=0.5, label='saturazione')
    axes[2].axhline(-F_MAX, color='r', linestyle=':', alpha=0.5)
    if switch_time is not None:
        axes[2].axvline(switch_time, color='gray', linestyle='--', alpha=0.6)
    axes[2].set_ylabel('F [N]')
    axes[2].set_xlabel('tempo [s]')
    axes[2].legend(); axes[2].grid(True)

    mode_str = "feedback (u=ubar+K*dx)" if FEEDBACK_ENABLED else "solo feedforward (u=ubar)"
    fig.suptitle(f'DDP swing-up + LQR upright — {mode_str}', fontsize=13)
    fig.tight_layout()
    fig.savefig('risultati_trajopt.png', dpi=150)
    plt.show()
    print("Plot salvato in risultati_trajopt.png")

    print(f"\nStato finale: x={data.qpos[0]:.4f} m, "
          f"theta={np.degrees(data.qpos[1]):.2f} deg, "
          f"dx={data.qvel[0]:.4f}, dtheta={data.qvel[1]:.4f}")


if __name__ == "__main__":
    main()