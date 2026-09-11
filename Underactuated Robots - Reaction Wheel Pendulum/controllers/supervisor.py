# Switching tra swingup e balance per il RWP
#
# CONVENZIONE: q1=0 -> pendolo in su (goal), q1=π -> in giù (partenza)
# Vincolo aggiuntivo: il balance FL è valido solo per |q1| < π/2
# (singolarità a q1=π/2, vedi paper Sez. 3.1)

import numpy as np

def should_switch_to_balance(q1, q2, dq1, dq2,
                              thr_pos=0.5, thr_vel=1.0):
    """
    Attiva il balance FL solo se:
      1. q1 vicino a 0 (ben dentro la regione |q1|<pi/2 di validità FL)
      2. velocità angolari non eccessive
    """
    q1n = np.arctan2(np.sin(q1), np.cos(q1))
    cond_pos = abs(q1n) < thr_pos
    cond_vel = abs(dq1) < thr_vel and abs(dq2) < thr_vel
    return cond_pos and cond_vel

def should_switch_to_swingup(q1, q2, dq1, dq2,
                              thr_pos=0.6, thr_vel=4.0):
    """
    Torna allo swingup se il balance perde il controllo
    (isteresi: soglie più larghe di should_switch_to_balance)
    """
    q1n = np.arctan2(np.sin(q1), np.cos(q1))
    cond_pos = abs(q1n) > thr_pos
    cond_vel = abs(dq1) > thr_vel or abs(dq2) > thr_vel
    return cond_pos or cond_vel

# ── Test rapido ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Test supervisor.py ===")

    r1 = should_switch_to_balance(np.pi, 0.0, 0.0, 0.0)
    print(f"q1=π, fermo -> switch a balance? {r1}  (atteso: False)")

    r2 = should_switch_to_balance(0.1, 0.0, 0.0, 0.0)
    print(f"q1=0.1, fermo -> switch a balance? {r2}  (atteso: True)")

    r3 = should_switch_to_balance(0.1, 0.0, 3.0, 0.0)
    print(f"q1=0.1, dq1=3.0 -> switch a balance? {r3}  (atteso: False, troppo veloce)")

    r4 = should_switch_to_swingup(0.4, 0.0, 0.5, 0.0)
    print(f"q1=0.4 (balance attivo) -> torna a swingup? {r4}  (atteso: False)")

    r5 = should_switch_to_swingup(0.7, 0.0, 0.5, 0.0)
    print(f"q1=0.7 (balance attivo) -> torna a swingup? {r5}  (atteso: True)")