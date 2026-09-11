# utils/params.py
# Parametri fisici del Reaction Wheel Pendulum (Spong-Corke-Lozano 2001)
#
# CONVENZIONE ANGOLI (confermata nel modello MuJoCo):
#   q1=0 -> pendolo verticale verso l'ALTO (equilibrio instabile, goal)
#   q1=π -> pendolo verticale verso il BASSO (equilibrio stabile, partenza)

# utils/params.py
import numpy as np

g = 9.8
mbar = 0.18   # invariato, dipende solo da m1*lc1+m2*l1 (masse e posizioni, non inerzie)

# Valori ESATTI letti dalla mass matrix reale di MuJoCo (q1=0,q2=0)
# tramite mj_fullM — eliminano ogni ambiguità di calcolo manuale
# delle inerzie per geometrie capsula/cilindro complesse.
d11 = 0.06659045238095238
d12 = 0.0021600000000000005
d22 = 0.0021600000000000005
detD = d11*d22 - d12**2

def phi(q1):
    return -mbar * g * np.sin(q1)

def total_energy(q1, dq1):
    return 0.5*d11*dq1**2 - mbar*g*(1-np.cos(q1))

def forward_dynamics(q1, q2, dq1, dq2, tau):
    ddq1 = -(d22/detD)*phi(q1) - (d12/detD)*tau
    ddq2 =  (d12/detD)*phi(q1) + (d11/detD)*tau
    return ddq1, ddq2

# ── Test rapido ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Test params.py (RWP) ===")
    print(f"d11={d11:.6f}  d12={d12:.6e}  d22={d22:.6e}  detD={detD:.6e}")
    print(f"mbar={mbar:.6f}")

    ddq1, ddq2 = forward_dynamics(0.05, 0.0, 0.0, 0.0, 0.0)
    print(f"\nCon q1=0.05, tau=0: ddq1={ddq1:.4f}  ddq2={ddq2:.4f}")
    print("(ddq1 deve essere POSITIVO: pendolo si allontana da q1=0)")

    E_top    = total_energy(0.0, 0.0)
    E_bottom = total_energy(np.pi, 0.0)
    print(f"\nE(q1=0, fermo)  = {E_top:.4f} J   (deve essere 0, goal)")
    print(f"E(q1=π, fermo)  = {E_bottom:.4f} J  (energia da pompare nello swingup)")