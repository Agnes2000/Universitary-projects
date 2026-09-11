# utils/params.py
# Parametri fisici del Convey-Crane (Collado-Lozano-Fantoni 2000)
# Convenzione: th=0 -> pendolo verticale verso il BASSO (target)

import numpy as np

M = 1.0   # massa carrello [kg]  - da <geom cart_body mass="1.0">
m = 1.0   # massa pendolo [kg]   - da <geom rod mass="1.0">
l = 1.0   # lunghezza pendolo [m]- da fromto 0 a -1.0
g = 9.8   # gravità [m/s^2]      - da <option gravity>

def forward_dynamics(x, dx, th, dth, F):
    """
    Equazioni (15)-(16) del paper:
    ddx  = (1/den) * [-m*l*sin(th)*(l*dth^2 + g*cos(th)) + F]
    ddth = (1/(l*den)) * [-sin(th)*((M+m)*g + m*l*cos(th)*dth^2) + cos(th)*F]
    den = M + m*sin(th)^2
    """
    den = M + m * np.sin(th)**2
    ddx  = (1.0/den) * (-m*l*np.sin(th)*(l*dth**2 + g*np.cos(th)) + F)
    ddth = (1.0/(l*den)) * (-np.sin(th)*((M+m)*g + m*l*np.cos(th)*dth**2) + np.cos(th)*F)
    return ddx, ddth

def total_energy(th, dth):
    """
    Energia del pendolo libero (eq. 8 del paper, parte cinetica
    + potenziale solo del pendolo, riferita all'equilibrio basso).
    E = (1/2)*m*l^2*dth^2 + m*g*l*(1-cos(th))
    """
    return 0.5*m*l**2*dth**2 + m*g*l*(1-np.cos(th))

# ── Test rapido ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Test params.py ===")
    ddx, ddth = forward_dynamics(0.0, 0.0, np.pi/4, 0.0, 0.0)
    print(f"Con th=45°, F=0, fermo: ddx={ddx:.4f}  ddth={ddth:.4f}")
    print("(ddth deve essere negativo: il pendolo cade verso th=0)")

    E = total_energy(np.pi/4, 0.0)
    print(f"\nEnergia a th=45°, fermo: E={E:.4f} J")
    print(f"Energia a th=0 (equilibrio): E={total_energy(0,0):.4f} J  (deve essere 0)")