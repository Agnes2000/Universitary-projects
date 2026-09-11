import mujoco
import numpy as np

model = mujoco.MjModel.from_xml_path("model/rwp.xml")
data = mujoco.MjData(model)

pend_id = model.body('pendulum').id
disk_id = model.body('disk').id

m1 = model.body_mass[pend_id]
m2 = model.body_mass[disk_id]

I1 = model.body_inertia[pend_id][1]   # componente Y (asse di rotazione q1)
I2 = model.body_inertia[disk_id][1]   # componente Y (asse di rotazione q2)

lc1 = abs(model.body_ipos[pend_id][2])   # CoM pendolo rispetto al suo giunto
l1  = abs(model.body_pos[disk_id][2])    # distanza pivot1->pivot2

print(f"m1={m1}  m2={m2}")
print(f"I1={I1:.6e}  I2={I2:.6e}")
print(f"lc1={lc1:.6f}  l1={l1:.6f}")

mbar = m1*lc1 + m2*l1
d11 = m1*lc1**2 + m2*l1**2 + I1 + I2
d12 = I2
d22 = I2
detD = d11*d22 - d12**2

print(f"\nmbar={mbar:.6f}")
print(f"d11={d11:.6f}  d12={d12:.6e}  d22={d22:.6e}  detD={detD:.6e}")
