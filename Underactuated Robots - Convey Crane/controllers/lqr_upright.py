# Controllore LQR per il Cart-Pole in configurazione UPRIGHT
# (stesso impianto fisico del Convey-Crane, ma equilibrio target
#  theta = pi, cioè pendolo verso l'ALTO, instabile)
#
# Riferimento fisico: stesse equazioni (15)-(16) di Collado-Lozano-
# Fantoni (2000), stesso file utils/params.py / forward_dynamics.
# Cambia solo il punto di linearizzazione.
#
# Variabile di deviazione: phi = theta - pi
#   phi=0  <-> theta=pi  (pendolo in alto, target)
#   Per phi piccolo: sin(theta) = sin(pi+phi) ≈ -phi
#                     cos(theta) = cos(pi+phi) ≈ -1
#
# Stato:  z = [x, dx, phi, dphi]^T   (phi = theta - pi)
# Ingresso: u = F
#
# Dinamica linearizzata:
#   ddx   = (-m*g*phi + F) / M
#   ddphi = ((M+m)*g*phi - F) / (M*l)
#
# Nota il segno OPPOSTO sul termine gravitazionale di ddphi rispetto
# al caso basso (lqr.py): qui l'equilibrio è instabile, una deviazione
# phi>0 viene amplificata (+) invece che richiamata a zero (-).

import numpy as np
from scipy.linalg import solve_continuous_are

from utils.params import M, m, l, g, forward_dynamics


def wrap_to_pi(angle):
    """Porta un angolo in (-pi, pi], per gestire l'accumulo continuo di theta in simulazione."""
    return ((angle + np.pi) % (2 * np.pi)) - np.pi


def theta_to_phi(theta):
    """
    Converte l'angolo assoluto theta (convenzione MuJoCo, theta=0 in basso)
    nella variabile di deviazione phi = theta - pi, con wrapping corretto
    in modo che phi sia sempre piccolo vicino all'equilibrio alto.
    """
    return wrap_to_pi(theta - np.pi)


def get_linearization():
    """
    Costruisce le matrici A, B della dinamica linearizzata
    attorno all'equilibrio ALTO (x, dx, phi, dphi) = (0,0,0,0),
    cioè theta = pi.

    Ritorna:
        A : ndarray (4,4)
        B : ndarray (4,1)
    """
    A = np.array([
        [0.0, 1.0,             0.0, 0.0],
        [0.0, 0.0,         -m*g/M, 0.0],
        [0.0, 0.0,             0.0, 1.0],
        [0.0, 0.0, (M+m)*g/(M*l), 0.0],
    ])
    B = np.array([
        [0.0],
        [1.0/M],
        [0.0],
        [-1.0/(M*l)],
    ])
    return A, B


def design_lqr(Q=None, R=None):
    """
    Risolve l'ARE continua e calcola K tale che u = -K @ z,
    con z = [x, dx, phi, dphi].

    Parametri:
        Q : peso sullo stato (4,4), default diag([1, 1, 10, 1])
            (nota: peso minore su x rispetto al caso basso, perché qui
            la priorità assoluta è non far cadere il pendolo, non
            riportare il carrello a x=0)
        R : peso sull'ingresso (1,1), default [[1]]

    Ritorna:
        K, A, B, P
    """
    A, B = get_linearization()

    if Q is None:
        Q = np.diag([1.0, 1.0, 10.0, 1.0])
    if R is None:
        R = np.array([[1.0]])

    P = solve_continuous_are(A, B, Q, R)
    K = np.linalg.inv(R) @ B.T @ P

    return K, A, B, P


def lqr_control(state, K):
    """
    Legge di controllo LQR per l'upright.

    Parametri:
        state : [x, dx, theta, dth] - stato GREZZO da MuJoCo, con
                theta nella convenzione assoluta (0=basso, pi=alto).
                La conversione a phi viene fatta internamente.
        K     : guadagno LQR (1,4), da design_lqr()

    Ritorna:
        F : forza di controllo (scalare)
    """
    x, dx, theta, dth = state
    phi = theta_to_phi(theta)
    z = np.array([[x], [dx], [phi], [dth]])
    F = -(K @ z)[0, 0]
    return F


def check_controllability(A, B):
    """Verifica il rank della matrice di controllabilità (deve essere 4)."""
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
    print("=== Test controllers/lqr_upright.py ===\n")

    A, B = get_linearization()
    print("Matrice A (upright):")
    print(A)
    print("\nMatrice B (upright):")
    print(B)

    rank, n = check_controllability(A, B)
    print(f"\nRank matrice di controllabilità: {rank}/{n}",
          "-> controllabile" if rank == n else "-> NON controllabile")

    K, A, B, P = design_lqr()
    print(f"\nGuadagno K = {K}")

    eigvals = np.linalg.eigvals(A - B @ K)
    print(f"\nAutovalori anello chiuso:\n{eigvals}")
    print("Stabile (tutte le parti reali < 0):", np.all(eigvals.real < 0))

    # ── Simulazione non lineare in loop chiuso ──────────────────────
    # Partenza vicino all'equilibrio alto: theta0 = pi + piccola perturbazione
    print("\n=== Simulazione non lineare in loop chiuso (upright) ===")
    dt = 0.001
    T = 8.0
    steps = int(T / dt)

    x, dx = 0.0, 0.0
    theta = np.pi + np.deg2rad(15.0)   # 15 gradi di scostamento dall'alto
    dth = 0.0

    F_max_seen = 0.0
    F_sat_count = 0
    for i in range(steps):
        state = [x, dx, theta, dth]
        F = lqr_control(state, K)
        F_max_seen = max(F_max_seen, abs(F))
        if abs(F) > 50.0:
            F_sat_count += 1

        ddx, ddth = forward_dynamics(x, dx, theta, dth, F)
        dx += ddx * dt
        x += dx * dt
        dth += ddth * dt
        theta += dth * dt

        if i % int(1.0 / dt) == 0:
            phi_deg = np.rad2deg(theta_to_phi(theta))
            print(f"t={i*dt:5.2f}s  x={x:7.4f}  phi={phi_deg:8.3f}°  F={F:8.3f}")

    phi_final = np.rad2deg(theta_to_phi(theta))
    print(f"\nStato finale: x={x:.6f}, dx={dx:.6f}, "
          f"phi={phi_final:.6f}° (theta={np.rad2deg(theta):.3f}°), dth={dth:.6f}")
    print(f"Forza massima richiesta: {F_max_seen:.2f} N "
          f"(limite attuatore: ±50 N)")
    print(f"Passi con |F| > 50N (saturazione, non gestita dall'LQR): {F_sat_count}/{steps}")