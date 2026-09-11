# Feedback Linearization esatta per il balance (Sezione 3.1 del paper)
#
# Output: y = h(x) = d11*x2 + d12*x3  (momento generalizzato, eq. 11)
# Relative degree = 3 rispetto a tau
# Coordinate trasformate: zeta1=h, zeta2=Lf(h), zeta3=Lf^2(h)
#
# Valido per |q1| < pi/2 (regione di linearizzabilita', vedi paper)

import numpy as np
from utils.params import d11, d12, d22, detD, mbar, g, phi

def compute_zeta(q1, dq1, dq2):
    """
    zeta1 = d11*dq1 + d12*dq2          (momento generalizzato)
    zeta2 = mbar*g*sin(q1)             (Lf h)
    zeta3 = mbar*g*cos(q1)*dq1         (Lf^2 h)
    """
    zeta1 = d11*dq1 + d12*dq2
    zeta2 = mbar*g*np.sin(q1)
    zeta3 = mbar*g*np.cos(q1)*dq1
    return zeta1, zeta2, zeta3

def Lf3h_and_LgLf2h(q1, dq1):
    """
    Lf^3 h e LgLf^2 h, necessari per calcolare tau (eq. 20).
    Usa phi() importato da utils.params per coerenza di segno
    con la dinamica reale verificata in MuJoCo.
    """
    phi_q1 = phi(q1)              # <-- usa la funzione importata, non ridefinita
    ddq1_free = -(d22/detD)*phi_q1

    Lf3h = -mbar*g*np.sin(q1)*dq1**2 + mbar*g*np.cos(q1)*ddq1_free
    LgLf2h = mbar*g*np.cos(q1) * (-d12/detD)
    return Lf3h, LgLf2h

def balance_control(q1, q2, dq1, dq2, k1=100.0, k2=50.0, k3=10.0):
    """
    Legge di controllo FL (eq. 20-24 del paper):
    u = -k1*zeta1 - k2*zeta2 - k3*zeta3   (assegna i poli in zeta-coordinate)
    tau = (u - Lf^3 h) / LgLf^2 h

    Valida per |q1| < pi/2 (altrimenti LgLf2h si annulla in q1=pi/2)
    """
    zeta1, zeta2, zeta3 = compute_zeta(q1, dq1, dq2)
    Lf3h, LgLf2h = Lf3h_and_LgLf2h(q1, dq1)

    u = -k1*zeta1 - k2*zeta2 - k3*zeta3
    tau = (u - Lf3h) / LgLf2h
    return tau

# ── Test rapido ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Test balance_fl.py ===")

    tau0 = balance_control(0.05, 0.0, 0.0, 0.0)
    print(f"tau con q1=0.05 (piccola deviazione), fermo: {tau0:.4f}")
    print("(deve essere tale da riportare il pendolo a q1=0)")

    tau1 = balance_control(-0.05, 0.0, 0.0, 0.0)
    print(f"\ntau con q1=-0.05: {tau1:.4f}")
    print("(deve essere opposto al caso precedente, per simmetria)")

    # Verifica singolarita' a q1=pi/2
    _, LgLf2h_sing = Lf3h_and_LgLf2h(np.pi/2 - 0.001, 0.0)
    print(f"\nLgLf2h vicino a q1=pi/2: {LgLf2h_sing:.6f}  (deve essere vicino a 0)")