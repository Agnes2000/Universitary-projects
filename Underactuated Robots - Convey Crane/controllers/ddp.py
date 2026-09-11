"""
Solver DDP/iLQR generico. Non conosce nulla del Convey-Crane specificamente:
lavora con qualunque sistema che fornisca dynamics_step, dynamics_jacobians,
running_cost (+ derivate), terminal_cost (+ derivate) — esattamente le
funzioni definite in controllers/trajopt_swingup.py. 

Riferimento teorico (per l'orale): equazione di Bellman, backward pass che
costruisce l'approssimazione quadratica locale della Q-function e della
value function, forward pass con line search — stessa struttura delle slide
di Scianca su Dynamic Programming / DDP.

Convenzioni dimensionali:
    stato x:  vettore (n,)
    input u:  vettore (m,)
    A = df/dx: matrice (n,n)
    B = df/du: matrice (n,m)
    k (feedforward): vettore (m,)
    K (feedback):    matrice (m,n)
"""

import numpy as np


def rollout(dynamics_step, x0, U, dt):
    """Simula in avanti la dinamica con la sequenza di ingressi U (N,m).
    Ritorna X (N+1, n)."""
    N = len(U)
    n = len(x0)
    X = np.zeros((N + 1, n))
    X[0] = x0
    for k in range(N):
        X[k + 1] = dynamics_step(X[k], U[k], dt)
    return X


def trajectory_cost(X, U, running_cost, terminal_cost):
    N = len(U)
    J = sum(running_cost(X[t], U[t]) for t in range(N))
    J += terminal_cost(X[-1])
    return J


def backward_pass(X, U, dynamics_jacobians, running_cost_grad, running_cost_hess,
                   terminal_cost_grad, terminal_cost_hess, dt, reg):
    """
    Un passo all'indietro del DDP: costruisce l'approssimazione quadratica
    locale di Q(x,u) ad ogni istante, ricava i guadagni k_t (feedforward) e
    K_t (feedback), e propaga la value function (Vx, Vxx) al passo precedente.

    reg: termine di regolarizzazione di Levenberg-Marquardt aggiunto a Quu
         (Quu_reg = Quu + reg*I) per garantirne l'invertibilita' e la
         positiva definitezza — necessario perche' lontano dall'ottimo, per
         un sistema non lineare, Quu non e' garantito positivo.

    Ritorna (k_list, K_list, success). Se success=False, il backward pass
    e' fallito (Quu non regolarizzabile a sufficienza) e va aumentato reg.
    """
    N = len(U)
    k_list = [None] * N
    K_list = [None] * N

    Vx = terminal_cost_grad(X[-1])
    Vxx = terminal_cost_hess(X[-1])

    for t in reversed(range(N)):
        x, u = X[t], U[t]
        A, B = dynamics_jacobians(x, u, dt)          # f^x, f^u
        l_x, l_u = running_cost_grad(x, u)
        l_xx, l_uu, l_ux = running_cost_hess(x, u)

        Qx = l_x + A.T @ Vx
        Qu = l_u + B.T @ Vx
        Qxx = l_xx + A.T @ Vxx @ A
        Quu = l_uu + B.T @ Vxx @ B
        Qux = l_ux + B.T @ Vxx @ A

        Quu_reg = Quu + reg * np.eye(Quu.shape[0])

        # Quu deve essere positiva definita perche' il punto stazionario
        # trovato risolvendo dQ/du=0 sia un MINIMO (vedi Newton's method /
        # convessita' nelle slide: Hessiano positivo -> minimo, altrimenti
        # si rischia di convergere verso un massimo o un punto sella)
        eigvals = np.linalg.eigvalsh(Quu_reg)
        if np.any(eigvals <= 0):
            return None, None, False

        Quu_inv = np.linalg.inv(Quu_reg)
        k = -Quu_inv @ Qu
        K = -Quu_inv @ Qux

        k_list[t] = k
        K_list[t] = K

        # Aggiornamento della value function (formule standard iLQR/DDP,
        # forma espansa — vedi slide "Aggiornamento della value function")
        Vx = Qx + K.T @ Quu @ k + K.T @ Qu + Qux.T @ k
        Vxx = Qxx + K.T @ Quu @ K + K.T @ Qux + Qux.T @ K
        Vxx = 0.5 * (Vxx + Vxx.T)  # forza simmetria numerica (accumulo errori float)

    return k_list, K_list, True


def forward_pass(X, U, k_list, K_list, dynamics_step, running_cost, terminal_cost, dt, alpha):
    """
    Un passo in avanti: applica u_t = u_t + alpha*k_t + K_t*(x_t_new - x_t_old),
    propaga la dinamica, e ricalcola il costo totale della nuova traiettoria.
    """
    N = len(U)
    n = X.shape[1]
    X_new = np.zeros_like(X)
    U_new = np.zeros_like(U)
    X_new[0] = X[0]

    for t in range(N):
        dx = X_new[t] - X[t]
        U_new[t] = U[t] + alpha * k_list[t] + K_list[t] @ dx
        X_new[t + 1] = dynamics_step(X_new[t], U_new[t], dt)

    J_new = trajectory_cost(X_new, U_new, running_cost, terminal_cost)
    return X_new, U_new, J_new


def solve_ddp(x0, U_init, dynamics_step, dynamics_jacobians,
              running_cost, running_cost_grad, running_cost_hess,
              terminal_cost, terminal_cost_grad, terminal_cost_hess,
              dt, max_iters=200, tol=1e-4, verbose=True):
    """
    Loop principale DDP: alterna backward pass e forward pass (con line
    search a dimezzamento, come nelle slide) fino a convergenza.

    Ritorna: X, U (traiettoria ottima), k_list, K_list (guadagni
    dell'ultimo backward pass, utili per il tracking closed-loop in
    main_trajopt.py), history (costo ad ogni iterazione accettata).
    """
    U = U_init.copy()
    X = rollout(dynamics_step, x0, U, dt)
    J = trajectory_cost(X, U, running_cost, terminal_cost)

    reg = 1e-6
    reg_max = 1e10
    reg_min = 1e-9
    k_list, K_list = None, None

    history = [J]
    if verbose:
        print(f"[iter -] costo iniziale = {J:.6f}")

    for it in range(max_iters):
        k_list, K_list, ok = backward_pass(
            X, U, dynamics_jacobians, running_cost_grad, running_cost_hess,
            terminal_cost_grad, terminal_cost_hess, dt, reg
        )
        if not ok:
            reg = min(reg * 10, reg_max)
            if verbose:
                print(f"[iter {it}] backward pass fallito (Quu non PD), reg -> {reg:.1e}")
            if reg >= reg_max:
                if verbose:
                    print("Regolarizzazione al limite massimo, interrompo.")
                break
            continue

        # Line search: alpha da 1, dimezzo finche' il costo decresce davvero
        # (stessa logica descritta nelle slide per il forward pass del DDP)
        alpha = 1.0
        improved = False
        for _ in range(10):
            X_new, U_new, J_new = forward_pass(
                X, U, k_list, K_list, dynamics_step, running_cost, terminal_cost, dt, alpha
            )
            if J_new < J:
                improved = True
                break
            alpha *= 0.5

        if not improved:
            reg = min(reg * 10, reg_max)
            if verbose:
                print(f"[iter {it}] line search fallita, reg -> {reg:.1e}")
            if reg >= reg_max:
                if verbose:
                    print("Regolarizzazione al limite massimo, interrompo.")
                break
            continue

        dJ = J - J_new
        X, U, J = X_new, U_new, J_new
        reg = max(reg * 0.5, reg_min)
        history.append(J)

        if verbose:
            print(f"[iter {it}] costo = {J:.6f}  (delta={dJ:.2e}, alpha={alpha:.3f}, reg={reg:.1e})")

        if abs(dJ) < tol:
            if verbose:
                print(f"Convergenza raggiunta dopo {it+1} iterazioni.")
            break

    return X, U, k_list, K_list, history