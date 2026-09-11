"""
Diagnostica: verifica che i file che stai effettivamente caricando siano
le versioni corrette (con la griglia abbassata/trasparente e il fix del
segno nel marker). Esegui con: python check_files.py dalla root di conveycrane.
"""
import mujoco

model = mujoco.MjModel.from_xml_path("model/cart_pole.xml")

floor_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
cart_id  = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "cart_body")

print("floor pos (atteso: [0, 0, -1]):      ", model.geom_pos[floor_id])
print("floor rgba (atteso alpha=0.35):      ", model.geom_rgba[floor_id])
print("cart pos nel body (atteso [0,0,1.5]):", model.body_pos[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'cart')])

print()
print("--- ora controllo utils/viz_helpers.py ---")
with open("utils/viz_helpers.py") as f:
    src = f.read()
if "x_target - l * np.sin" in src:
    print("OK: il fix del segno (px = x_target - l*sin(theta)) e' presente.")
elif "x_target + l * np.sin" in src:
    print("PROBLEMA: e' ancora presente la versione VECCHIA (con +), il file non e' stato sostituito.")
else:
    print("Non trovo ne' la vecchia ne' la nuova riga: controlla se il file e' proprio quello giusto.")