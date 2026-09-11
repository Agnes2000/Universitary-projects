"""
utils/viz_helpers.py

Funzioni di visualizzazione condivise (marker per la posizione target, ecc.)
usate da main.py, main_lqr.py, main_upright.py.
"""

import mujoco
import numpy as np


def add_target_marker(viewer, *, x_target, theta_target, l=1.0, cart_height=1.5):
    """
    Disegna nel viewer un marker semi-trasparente per la posizione desiderata:
    - una sfera verde sulla posizione target del carrello
    - un segmento verde che mostra l'angolo target del pendolo

    Chiamala UNA SOLA VOLTA, subito dopo aver aperto il viewer, prima del
    while loop di simulazione (i geom aggiunti restano fissi per tutta la
    sessione — non serve richiamarla ad ogni frame).

    Parametri:
        viewer:       l'oggetto restituito da mujoco.viewer.launch_passive(...)
        x_target:     posizione desiderata del carrello [m]
        theta_target: angolo desiderato del pendolo [rad]
                      (0 = equilibrio basso, pi = equilibrio alto)
        l:            lunghezza del pendolo [m] (default 1.0, come nel tuo modello)
        cart_height:  altezza del centro del carrello sull'asse z [m].
                      Default 1.5, coerente con <body name="cart" pos="0 0 1.5">
                      nel cart_pole.xml aggiornato. Se in futuro cambi quella
                      quota nell'XML, aggiornala anche qui.

    NOTA: x_target e theta_target sono keyword-only (dopo il *) apposta:
    cosi' una chiamata posizionale sbagliata da' un TypeError esplicito
    invece di eseguire silenziosamente con i due valori scambiati.
    """
    scn = viewer.user_scn
    i = scn.ngeom

    # Sfera sulla posizione desiderata del carrello
    mujoco.mjv_initGeom(
        scn.geoms[i], type=mujoco.mjtGeom.mjGEOM_SPHERE,
        size=[0.05, 0, 0], pos=[x_target, 0, cart_height],
        mat=np.eye(3).flatten(), rgba=[0, 1, 0, 0.4]
    )
    i += 1

    # Segmento che mostra l'angolo desiderato del pendolo
    # NOTA: il segno di px e' -l*sin(theta), non +l*sin(theta) — verificato
    # contro la posizione reale del bob in MuJoCo (il hinge ruota il rod
    # in modo che l'offset dal pivot sia (-l*sin(theta), 0, -l*cos(theta))).
    px = x_target - l * np.sin(theta_target)
    pz = cart_height - l * np.cos(theta_target)
    mujoco.mjv_initGeom(
        scn.geoms[i], type=mujoco.mjtGeom.mjGEOM_CAPSULE,
        size=[0.015, 0, 0], pos=[0, 0, 0], mat=np.eye(3).flatten(),
        rgba=[0, 1, 0, 0.3]
    )
    mujoco.mjv_connector(
        scn.geoms[i], mujoco.mjtGeom.mjGEOM_CAPSULE, 0.015,
        [x_target, 0, cart_height], [px, 0, pz]
    )
    i += 1

    # "Pallina" verde sulla posizione target del bob (px, pz) — questo e'
    # il marker che segue davvero theta_target: giu' per theta_target=0,
    # su per theta_target=pi. Stessa dimensione della pallina gialla reale
    # (size 0.08 nel tuo cart_pole.xml) cosi' sono visivamente confrontabili.
    mujoco.mjv_initGeom(
        scn.geoms[i], type=mujoco.mjtGeom.mjGEOM_SPHERE,
        size=[0.08, 0, 0], pos=[px, 0, pz],
        mat=np.eye(3).flatten(), rgba=[0, 1, 0, 0.5]
    )
    i += 1

    scn.ngeom = i