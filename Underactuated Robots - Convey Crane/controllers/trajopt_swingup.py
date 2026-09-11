"""
NOTA IMPORTANTE:
Questo modulo NON usa MuJoCo. Usa il modello analitico del paper
(Collado-Lozano-Fantoni 2000, eqs. 15-16), stessi valori numerici di
utils/params.py, discretizzato con Eulero in avanti. Il DDP ha bisogno
di un modello chiuso, differenziabile in forma analitica per fare il
backward pass; MuJoCo entra in gioco solo dopo, in main_trajopt.py,
per simulazione e tracking.

Stato:   x = [x_cart, theta, dx_cart, dtheta]
Input:   u = [F]
Start:   x0      = [0, 0, 0, 0]    (equilibrio basso, stabile)
Target:  x_goal  = [0, pi, 0, 0]   (equilibrio alto, instabile)
"""

import numpy as np
import sympy as sp

# ---------------------------------------------------------------------------
# 1. Parametri fisici
# ---------------------------------------------------------------------------
M_val = 1.0    # massa carrello [kg]
m_val = 1.0    # massa pendolo [kg]
l_val = 1.0    # lunghezza pendolo [m]
g_val = 9.8    # gravita' [m/s^2]
DT    = 0.02   # passo di discretizzazione per il DDP (NON e' il dt di MuJoCo, che resta 0.001)

# ---------------------------------------------------------------------------
# 2. Dinamica continua simbolica (eqs. 15-16, Collado-Lozano-Fantoni 2000)
# ---------------------------------------------------------------------------
x_s, th_s, dx_s, dth_s, F_s = sp.symbols('x theta dx dtheta F')
M_s, m_s, l_s, g_s = sp.symbols('M m l g')

den = M_s + m_s * sp.sin(th_s)**2

ddx  = (1/den) * (-m_s*l_s*sp.sin(th_s)*(l_s*dth_s**2 + g_s*sp.cos(th_s)) + F_s)
ddth = (1/(l_s*den)) * (-sp.sin(th_s)*((M_s+m_s)*g_s + m_s*l_s*sp.cos(th_s)*dth_s**2) + sp.cos(th_s)*F_s)

state_sym = sp.Matrix([x_s, th_s, dx_s, dth_s])
input_sym = sp.Matrix([F_s])

f_continuous = sp.Matrix([dx_s, dth_s, ddx, ddth])   # xdot = f_c(x, u)

# ---------------------------------------------------------------------------
# 3. Discretizzazione con Eulero in avanti: x_{k+1} = x_k + DT * f_c(x_k, u_k)
#  
# ---------------------------------------------------------------------------
dt_s = sp.symbols('dt')
f_discrete = state_sym + dt_s * f_continuous          # x_{k+1} simbolico

# Jacobiani simbolici del passo discreto (quello che serve al DDP: f^x, f^u)
A_sym = f_discrete.jacobian(state_sym)   # shape (4,4)
B_sym = f_discrete.jacobian(input_sym)   # shape (4,1)

# Sostituisco i parametri fisici numerici, lascio liberi x, theta, dx, dtheta, F, dt
params_subs = {M_s: M_val, m_s: m_val, l_s: l_val, g_s: g_val}
f_discrete_num = f_discrete.subs(params_subs)
A_num = A_sym.subs(params_subs)
B_num = B_sym.subs(params_subs)

_args = (x_s, th_s, dx_s, dth_s, F_s, dt_s)

# Funzioni numeriche veloci (lambdify -> nessun overhead simbolico a runtime,
# fondamentale perche' il DDP le chiama migliaia di volte per iterazione)
_f_func = sp.lambdify(_args, f_discrete_num, 'numpy')
_A_func = sp.lambdify(_args, A_num, 'numpy')
_B_func = sp.lambdify(_args, B_num, 'numpy')


def dynamics_step(x, u, dt=DT):
    """x_{k+1} = f(x_k, u_k). x: array (4,), u: array (1,) o scalare."""
    F = float(u[0]) if hasattr(u, '__len__') else float(u)
    out = _f_func(x[0], x[1], x[2], x[3], F, dt)
    return np.array(out, dtype=float).flatten()


def dynamics_jacobians(x, u, dt=DT):
    """Ritorna (A, B) = (df/dx, df/du) valutati in (x_k, u_k)."""
    F = float(u[0]) if hasattr(u, '__len__') else float(u)
    A = np.array(_A_func(x[0], x[1], x[2], x[3], F, dt), dtype=float)
    B = np.array(_B_func(x[0], x[1], x[2], x[3], F, dt), dtype=float)
    return A, B


# ---------------------------------------------------------------------------
# 4. Costo: running cost + terminal cost (entrambi quadratici -> derivate banali,
#    esattamente i termini che il backward pass del DDP si aspetta: l_x, l_u,
#    l_xx, l_uu, l_ux)
# ---------------------------------------------------------------------------
R_WEIGHT   = 0.01                              # peso su u^2 nel running cost
EPS_X      = 0.001                             # piccola regolarizzazione su x_cart (evita che scappi troppo)
Q_TERMINAL = np.diag([10.0, 800.0, 10.0, 150.0])  # peso terminale su (x, theta, dx, dtheta)
X_GOAL     = np.array([0.0, np.pi, 0.0, 0.0])  # equilibrio alto (target dello swing-up)

# NOTA SUL TUNING: questi pesi sono stati verificati con N=350 step (dt=0.02,
# quindi orizzonte di 7s) -> convergenza a theta=179.6°, x=-0.003, velocita'
# residue trascurabili, u_max=4N. Con orizzonti piu' corti (es. N=150) il DDP
# converge comunque (il costo smette di scendere) ma si ferma PRIMA di
# arrivare al target — non e' un bug, e' semplicemente un minimo locale
# raggiungibile in quel tempo: il DDP e' un metodo locale, non garantisce il
# raggiungimento esatto del target, solo la stazionarieta' rispetto al costo
# dato. Se cambi N, e' normale dover ritoccare Q_TERMINAL.


def running_cost(x, u):
    F = float(u[0]) if hasattr(u, '__len__') else float(u)
    return R_WEIGHT * F**2 + EPS_X * x[0]**2


def running_cost_grad(x, u):
    """Ritorna (l_x, l_u), entrambi shape coerenti con x (4,) e u (1,)."""
    F = float(u[0]) if hasattr(u, '__len__') else float(u)
    l_x = np.array([2*EPS_X*x[0], 0.0, 0.0, 0.0])
    l_u = np.array([2*R_WEIGHT*F])
    return l_x, l_u


def running_cost_hess(x, u):
    """Ritorna (l_xx, l_uu, l_ux) — costanti per un costo quadratico puro."""
    l_xx = np.diag([2*EPS_X, 0.0, 0.0, 0.0])
    l_uu = np.array([[2*R_WEIGHT]])
    l_ux = np.zeros((1, 4))
    return l_xx, l_uu, l_ux


def terminal_cost(x):
    dx = x - X_GOAL
    return dx @ Q_TERMINAL @ dx


def terminal_cost_grad(x):
    dx = x - X_GOAL
    return 2 * Q_TERMINAL @ dx


def terminal_cost_hess(x):
    return 2 * Q_TERMINAL


# ---------------------------------------------------------------------------
# 5. Sanity check 
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    x_test = np.array([0.1, 0.3, 0.05, -0.2])
    u_test = np.array([2.0])

    x_next = dynamics_step(x_test, u_test)
    A, B = dynamics_jacobians(x_test, u_test)

    eps = 1e-6
    A_fd = np.zeros((4, 4))
    for i in range(4):
        xp = x_test.copy(); xp[i] += eps
        xm = x_test.copy(); xm[i] -= eps
        A_fd[:, i] = (dynamics_step(xp, u_test) - dynamics_step(xm, u_test)) / (2*eps)

    B_fd = np.zeros((4, 1))
    up = u_test + eps
    um = u_test - eps
    B_fd[:, 0] = (dynamics_step(x_test, up) - dynamics_step(x_test, um)) / (2*eps)

    print("x_next:", x_next)
    print("max errore A (simbolico vs differenze finite):", np.max(np.abs(A - A_fd)))
    print("max errore B (simbolico vs differenze finite):", np.max(np.abs(B - B_fd)))
    print("costo running di test:", running_cost(x_test, u_test))
    print("costo terminale di test:", terminal_cost(x_test))