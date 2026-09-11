"""
Validazione offline del DDP sullo swing-up del Convey-Crane. Nessun MuJoCo
qui: usa solo il modello analitico (trajopt_swingup.py) + il solver
(ddp.py). Serve a verificare che il DDP converga PRIMA di collegarlo a
MuJoCo in main_trajopt.py.

"""

import numpy as np
import matplotlib.pyplot as plt

from controllers import trajopt_swingup as ts
from controllers import ddp


def main():
    N = 350                     # passi dell'orizzonte (con DT=0.02 -> 7s)
    x0 = np.array([0.0, 0.0, 0.0, 0.0])
    U_init = np.zeros((N, 1))

    print("Avvio DDP...")
    X, U, k_list, K_list, history = ddp.solve_ddp(
        x0, U_init,
        ts.dynamics_step, ts.dynamics_jacobians,
        ts.running_cost, ts.running_cost_grad, ts.running_cost_hess,
        ts.terminal_cost, ts.terminal_cost_grad, ts.terminal_cost_hess,
        ts.DT, max_iters=150, tol=1e-6, verbose=True
    )

    theta_finale_deg = np.degrees(X[-1][1])
    print()
    print(f"Stato finale: x={X[-1][0]:.4f} m, theta={theta_finale_deg:.2f} deg "
          f"(target 180 deg), dx={X[-1][2]:.4f}, dtheta={X[-1][3]:.4f}")
    print(f"u_max = {np.max(np.abs(U)):.2f} N  (limite attuatore: 50 N)")

    # --- Plot, stesso stile delle main esistenti (pannelli multipli + PNG) ---
    t = np.arange(N + 1) * ts.DT

    fig, axs = plt.subplots(4, 1, figsize=(8, 10), sharex=True)

    axs[0].plot(t, X[:, 0])
    axs[0].axhline(ts.X_GOAL[0], color='g', linestyle='--', label='target')
    axs[0].set_ylabel('x carrello [m]')
    axs[0].legend()
    axs[0].grid(alpha=0.3)

    axs[1].plot(t, np.degrees(X[:, 1]))
    axs[1].axhline(np.degrees(ts.X_GOAL[1]), color='g', linestyle='--', label='target')
    axs[1].set_ylabel('theta [deg]')
    axs[1].legend()
    axs[1].grid(alpha=0.3)

    axs[2].plot(t, X[:, 2], label='dx')
    axs[2].plot(t, X[:, 3], label='dtheta')
    axs[2].set_ylabel('velocita')
    axs[2].legend()
    axs[2].grid(alpha=0.3)

    axs[3].plot(t[:-1], U[:, 0])
    axs[3].axhline(50, color='r', linestyle=':', alpha=0.5)
    axs[3].axhline(-50, color='r', linestyle=':', alpha=0.5)
    axs[3].set_ylabel('F [N]')
    axs[3].set_xlabel('tempo [s]')
    axs[3].grid(alpha=0.3)

    fig.suptitle(f'DDP swing-up Convey-Crane — costo finale={history[-1]:.2f}, '
                 f'{len(history)} iterazioni')
    fig.tight_layout()
    fig.savefig('ddp_swingup_offline.png', dpi=120)
    print("\nPlot salvato in ddp_swingup_offline.png")

    # Plot separato della convergenza del costo (utile per l'orale: mostra
    # la monotonicita' della discesa, tipica del DDP con line search)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(history, marker='o', markersize=3)
    ax2.set_xlabel('iterazione')
    ax2.set_ylabel('costo totale J')
    ax2.set_title('Convergenza del costo DDP')
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig('ddp_convergence.png', dpi=120)
    print("Plot salvato in ddp_convergence.png")

    return X, U, k_list, K_list, history


if __name__ == "__main__":
    main()