# Swingup basato su passivita' (eq. 35-41 del paper)
#
# Usa il PFBLC (eq. 29-32) per ottenere: ddq2 = u (ingresso libero)
# Poi usa Lyapunov V = (ke/2)*E^2 + (kv/2)*dq2^2  per pompare energia

import numpy as np
from utils.params import d11, d12, d22, detD, mbar, g, total_energy

def pfbl_tau(q1, dq1, dq2, u):
    """
    Partial Feedback Linearization Collocata (eq. 29 del paper):
    Impone ddq2 = u, calcola tau corrispondente.

    Dalla dinamica (eq. 8): ddq2 = (d12/detD)*phi(q1) + (d11/detD)*tau
    Risolvendo per tau quando ddq2=u:
        tau = (u - (d12/detD)*phi(q1)) * (detD/d11)
            = u*(detD/d11) - (d12/d11)*phi(q1)
    """
    phi_q1 = -mbar*g*np.sin(q1)
    tau = u*(detD/d11) - (d12/d11)*phi_q1
    return tau

def swingup_control(q1, q2, dq1, dq2, ke=5000.0, kv=1.0):
    """
    Legge di controllo energetico (eq. 39 del paper):
    u = d12 * ke * E * dq1 - kv * dq2

    dove E e' l'energia del pendolo libero (eq. 35), riferita
    all'equilibrio INSTABILE (q1=0, E=0 li').

    NOTA SEGNO: nel nostro caso q1=0 e' il GOAL (instabile, in alto),
    quindi vogliamo E -> 0.
    """
    E = total_energy(q1, dq1)   # E=0 a q1=0 (goal), E>0 altrove

    u = d12 * ke * E * dq1 - kv * dq2
    tau = pfbl_tau(q1, dq1, dq2, u)
    return tau

# ── Test rapido ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Test swingup.py ===")

    from utils.params import total_energy
    E_bottom = total_energy(np.pi, 0.0)
    print(f"E(q1=π, fermo) = {E_bottom:.4f} J  (energia da dissipare verso 0)")

    tau0 = swingup_control(np.pi, 0.0, 0.0, 0.0)
    print(f"\ntau con q1=π, fermo: {tau0:.4f}")
    print("(deve essere ~0: dq1=0 -> nessun pompaggio possibile senza perturbazione)")

    tau1 = swingup_control(np.pi, 0.0, 0.5, 0.0)
    print(f"\ntau con q1=π, dq1=0.5: {tau1:.4f}")
    print("(deve essere diverso da zero: ora puo' pompare energia)")