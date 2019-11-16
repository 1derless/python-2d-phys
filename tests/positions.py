from phys import *
from base import *

DT = 0.01
ITERATIONS = 1000

world = System()

objs = (Projectile(pos=Vec(x=0, y=0), mass=10),
        Projectile(pos=Vec(x=100, y=100), mass=20),
        Projectile(pos=Vec(x=0, y=50), mass=0.1))

sprs = (Spring(stiffness=0.5, end1=objs[0], end2=objs[1]),
        Spring(stiffness=0.75, end1=objs[1], end2=objs[2]))

world.add_ent(*objs)
world.add_spring(*sprs)

for i in range(ITERATIONS):
    if i % 10 == 0:
        print(f'Iteration: {i}')
        print(world.get_state())

    world.update(DT)
