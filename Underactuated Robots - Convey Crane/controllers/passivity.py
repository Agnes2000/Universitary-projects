# controllers/passivity.py
# Legge di controllo basata su passività (Collado-Lozano-Fantoni 2000)
# Eq. (19) del paper: f = -(1/kE)*(kx*x + gamma*dx)
#
# Deriva da:
#   V(q,dq) = (kE/2)*E(q,dq) + (kx/2)*x^2
#   V_dot = -gamma*dx^2  (negativo semidefinito)
# garantendo convergenza a (x,dx,th,dth)=(0,0,0,0) per LaSalle,
# eccetto l'unico punto instabile (0,0,pi,0) [misura nulla].

import numpy as np

# Guadagni esattamente come nel paper (Sezione 5)
kE    = 1.0
kx    = 3.0
gamma = 4.3

def control_law(x, dx, th, dth):
    """
    f = -(1/kE) * (kx*x + gamma*dx)

    Nota: la legge dipende SOLO da x e dx (posizione/velocità
    del carrello) — non da th, dth direttamente! L'effetto sul
    pendolo è indiretto, tramite l'accoppiamento dinamico.
    """
    F = -(1.0/kE) * (kx*x + gamma*dx)
    return F

# ── Test rapido ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Test passivity.py ===")

    F1 = control_law(x=-5.0, dx=0.0, th=-np.pi/4, dth=0.0)
    print(f"F(x=-5, dx=0) = {F1:.4f} N")
    print("(deve essere positivo: spinge il carrello verso x=0)")

    F2 = control_law(x=5.0, dx=0.0, th=0.0, dth=0.0)
    print(f"\nF(x=5, dx=0) = {F2:.4f} N")
    print("(deve essere negativo: simmetrico al caso precedente)")

    F3 = control_law(x=0.0, dx=2.0, th=0.0, dth=0.0)
    print(f"\nF(x=0, dx=2.0) = {F3:.4f} N")
    print("(deve essere negativo: frena il carrello in moto)")