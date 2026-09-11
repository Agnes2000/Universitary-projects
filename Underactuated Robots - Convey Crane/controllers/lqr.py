# Controllore LQR per il Convey-Crane (Collado-Lozano-Fantoni 2000)
# Linearizzazione attorno all'equilibrio basso (x, dx, th, dth) = (0,0,0,0)
#
# Stato:  z = [x, dx, th, dth]^T
# Ingresso: u = F (forza sul carrello)
#
# Dinamica linearizzata (per piccoli th, dth):
#   ddx  = (-m*g*th + F) / M
#   ddth = (-(M+m)*g*th + F) / (M*l)

import numpy as np
from scipy.linalg import solve_continuous_are

from utils.params import M, m, l, g, forward_dynamics


def get_linearization():
    """
    Costruisce le matrici A, B della dinamica linearizzata
    attorno all'equilibrio basso (0,0,0,0).

    Ritorna:
        A : ndarray (4,4)
        B : ndarray (4,1)
    """
    A = np.array([
        [0.0, 1.0,            0.0, 0.0],
        [0.0, 0.0,        -m*g/M, 0.0],
        [0.0, 0.0,            0.0, 1.0],
        [0.0, 0.0, -(M+m)*g/(M*l), 0.0],
    ])
    B = np.array([
        [0.0],
        [1.0/M],
        [0.0],
        [1.0/(M*l)],
    ])
    return A, B


def design_lqr(Q=None, R=None):
    """
    Risolve l'equazione algebrica di Riccati continua e calcola
    il guadagno K tale che u = -K @ z.

    Parametri:
        Q : matrice di peso sullo stato (4,4), default diag([10, 1, 10, 1])
        R : peso sull'ingresso (1,1), default [[1]]

    Ritorna:
        K : ndarray (1,4) - guadagno LQR
        A, B : matrici della linearizzazione (per riferimento/debug)
        P : soluzione dell'equazione di Riccati
    """
    A, B = get_linearization()

    if Q is None:
        Q = np.diag([10.0, 1.0, 10.0, 1.0])
    if R is None:
        R = np.array([[1.0]])

    # Equazione algebrica di Riccati continua:
    #   A^T P + P A - P B R^-1 B^T P + Q = 0
    P = solve_continuous_are(A, B, Q, R)

    # Guadagno: K = R^-1 B^T P
    K = np.linalg.inv(R) @ B.T @ P

    return K, A, B, P


def lqr_control(z, K):
    """
    Legge di controllo LQR: u = -K @ z

    Parametri:
        z : array-like, stato [x, dx, th, dth]
        K : guadagno LQR (1,4), da design_lqr()

    Ritorna:
        F : forza di controllo (scalare)
    """
    z = np.asarray(z).reshape(4, 1)
    F = -(K @ z)[0, 0]
    return F


def check_controllability(A, B):
    """
    Verifica il rank della matrice di controllabilità.
    Il sistema è controllabile se rank == n (dimensione dello stato).
    """
    n = A.shape[0]
    C = B
    Ak = np.eye(n)
    for _ in range(1, n):
        Ak = Ak @ A
        C = np.hstack([C, Ak @ B])
    rank = np.linalg.matrix_rank(C)
    return rank, n


# ── Test rapido ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Test controllers/lqr.py ===\n")

    A, B = get_linearization()
    print("Matrice A:")
    print(A)
    print("\nMatrice B:")
    print(B)

    rank, n = check_controllability(A, B)
    print(f"\nRank matrice di controllabilità: {rank}/{n}",
          "-> controllabile" if rank == n else "-> NON controllabile")

    K, A, B, P = design_lqr()
    print(f"\nGuadagno K = {K}")

    # Autovalori del sistema in anello chiuso (devono avere parte reale < 0)
    eigvals = np.linalg.eigvals(A - B @ K)
    print(f"\nAutovalori anello chiuso:\n{eigvals}")
    print("Stabile (tutte le parti reali < 0):",
          np.all(eigvals.real < 0))

    # ── Simulazione in loop chiuso con la dinamica NON lineare vera ──
    # (usa forward_dynamics da params.py, non la linearizzazione)
    print("\n=== Simulazione non lineare in loop chiuso ===")
    dt = 0.001
    T = 8.0
    steps = int(T / dt)

    # Condizione iniziale: stessa usata nel test del passivity controller
    x, dx, th, dth = -5.0, 0.0, np.deg2rad(-45.0), 0.0

    F_max_seen = 0.0
    for i in range(steps):
        z = [x, dx, th, dth]
        F = lqr_control(z, K)
        F_max_seen = max(F_max_seen, abs(F))

        ddx, ddth = forward_dynamics(x, dx, th, dth, F)

        # Integrazione Euler semplice
        dx += ddx * dt
        x  += dx * dt
        dth += ddth * dt
        th  += dth * dt

        if i % int(1.0/dt) == 0:
            print(f"t={i*dt:5.2f}s  x={x:7.4f}  th={np.rad2deg(th):8.3f}°  F={F:8.3f}")

    print(f"\nStato finale: x={x:.6f}, dx={dx:.6f}, "
          f"th={np.rad2deg(th):.6f}°, dth={dth:.6f}")
    print(f"Forza massima richiesta durante il transitorio: {F_max_seen:.2f} N")