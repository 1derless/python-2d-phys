from base import *
from collision import *
from phys import *

__all__ = ['Collider', 'CollidingWorld', 'Material']


class Material:
    def __init__(self, static_friction, dynamic_friction, restitution, density):
        self.static_friction = static_friction
        self.dynamic_friction = dynamic_friction
        self.restitution = restitution
        self.density = density

    def to_dict(self):
        return {'static_friction' : self.static_friction,
                'dynamic_friction': self.dynamic_friction,
                'restitution'     : self.restitution,
                'density'         : self.density}

    @classmethod
    def from_dict(cls, d):
        return cls(
            static_friction=d['static_friction'],
            dynamic_friction=d['dynamic_friction'],
            restitution=d['restitution'],
            density=d['density']
        )


class Collider(Entity):
    def __init__(self, shape, material, pos, ang, mass, moi, vel=Vec(), acc=Vec(), ang_vel=0, ang_acc=0):
        # todo: auto-calculate mass and moi
        super().__init__(pos, mass, ang, moi, vel, acc, ang_vel, ang_acc)
        self.vertices = shape
        self.material = material

    def get_vertices(self):
        return [vertex.rotate(self.ang) + self.pos for vertex in self.vertices]

    def to_dict(self):
        d = super().to_dict()
        d.update(
            {'material': str(id(self.material)),
             'shape'   : str(id(self.vertices))}
        )

        return d

    @classmethod
    def from_dict(cls, d, id_, shapes, materials, *args, **kwargs):
        return cls(
            mass=d['mass'],
            pos=Vec.from_dict(d['pos']),
            vel=Vec.from_dict(d['vel']),
            acc=Vec.from_dict(d['acc']),
            moi=d['moi'],
            ang=d['ang'],
            ang_vel=d['ang_vel'],
            ang_acc=d['ang_acc'],
            shape=shapes[d['shape']],
            material=materials[d['material']],
        )


class CollidingWorld(World):
    def __init__(self, gravity=Vec(0, 0)):
        super().__init__(gravity)
        self.imps = []  # Impulse tracking for the visualisation.

    def add_ent(self, *objs):
        for obj in objs:
            if not isinstance(obj, Collider):
                raise TypeError(f"{obj} is not a Collider")

            super().add_ent(obj)

    def update(self, dt):
        # import random; random.shuffle(self.entities)
        self.imps = [imp[:3] + [imp[3] - 1] for imp in self.imps if imp[3] > 0]
        if len(self.imps) > 30:
            self.imps = self.imps[:31]

        self.damp(dt)
        self.update_spring(dt)
        self.update_collision(dt)
        self.update_turn(dt)
        self.update_move(dt)

    def update_collision(self, dt):
        def apply_impulse(entity, impulse, collision_normal, show=True):
            if entity.mass == float('inf'):
                return

            entity.new_vel += impulse / entity.mass
            entity.new_ang_vel += collision_normal.cross(impulse) / entity.moi

            if show:
                self.imps.append([entity.pos, impulse, collision_normal, 30])

        def correct_positions(o1, o2, separation, collision_normal):
            if o1.mass == float('inf') and o2.mass == float('inf'):
                return

            # Correct position for rounding errors.
            slop = 0
            error = 0.4
            if separation < -slop:
                correction = error * (-separation - slop) / (
                             1/o1.mass + 1/o2.mass) * collision_normal
                # o1.vel = max(1 / o1.mass * correction * dt, o1.vel, key=abs)
                # o2.vel = max(1 / o2.mass * correction * dt, o2.vel, key=abs)
                o1.new_pos -= 1 / o1.mass * correction
                o2.new_pos += 1 / o2.mass * correction

        def resolve(o1: Collider, o2: Collider, contact_normal):
            if o1.mass == float('inf') and o2.mass == float('inf'):
                return

            n = contact_normal

            # Find some point in space to apply the torque from on each
            # object relative to each object.
            pos = get_intersector(o1.get_vertices(), o2.get_vertices(), n)
            if pos is None:
                return
            pos_o1 = pos - o1.pos
            pos_o2 = pos - o2.pos

            dv = o2.vel + Vec(x=-o2.ang_vel * pos_o2.y, y=o2.ang_vel * pos_o2.x) - (
                 o1.vel + Vec(x=-o1.ang_vel * pos_o1.y, y=o1.ang_vel * pos_o1.x))

            inverse_mass_sum = (1/o1.mass
                                + 1/o2.mass
                                + (pos_o1.cross(n))**2 / o1.moi
                                + (pos_o2.cross(n))**2 / o2.moi)

            v_dot_n = dv.dot(n)

            if v_dot_n > 0.0:
                # If the two objects are moving away from each other,
                # then they are already going out of collision.
                return

            # Calculate scalar impulse, j.
            # Combine coef. of restitution
            e = min(o1.material.restitution, o2.material.restitution)
            j = -(1 + e) * v_dot_n
            j /= inverse_mass_sum

            # Apply impulse.
            # This ignores the velocity Verlet because collisions do not
            # apply steady or smooth forces.
            impulse = j * n
            apply_impulse(o1, -impulse, pos_o1)
            apply_impulse(o2, impulse, pos_o2)

            # Calculate and apply friction.
            # Combine coef. of static friction.
            mu = (o1.material.static_friction ** 2
                  + o2.material.static_friction ** 2
                  ) ** 0.5

            # Update as dv should have changed.
            dv = o2.new_vel + Vec(x=-o2.new_ang_vel * pos_o2.y, y=o2.new_ang_vel * pos_o2.x) - (
                 o1.new_vel + Vec(x=-o1.new_ang_vel * pos_o1.y, y=o1.new_ang_vel * pos_o1.x))
            t = dv - n * dv.dot(n)

            if abs(t) == 0:
                return
            t /= abs(t)

            jt = -dv.dot(t)  # Scalar impulse along tangent
            jt /= inverse_mass_sum

            if abs(jt) < j * mu:
                # Object is nearly at rest, apply static friction.
                impulse = jt * t
            else:
                # Object is not nearly at rest, apply dynamic friction.
                mu_dynamic = (o1.material.dynamic_friction ** 2
                              + o2.material.dynamic_friction ** 2
                              ) ** 0.5
                impulse = t * -j * mu_dynamic

            apply_impulse(o1, -impulse, pos_o1)
            apply_impulse(o2, impulse, pos_o2)

        collisions = collide_all(self.entities)
        for o1, o2, separation, normal in collisions:
            resolve(o1, o2, normal)

        for o1, o2, separation, normal in collisions:
            correct_positions(o1, o2, separation, normal)

    def to_dict(self):
        d = super().to_dict()

        # Assemble dict of shapes.
        shapes = {}
        for ent in self.entities:
            shapes[str(id(ent.vertices))] = ent.vertices

        # Assemble dict of materials in the same way.
        materials = {}
        for ent in self.entities:
            materials[str(id(ent.material))] = ent.material

        d.update(
            {'shapes'   : shapes,
             'materials': materials}
        )

        return d

    @classmethod
    def from_dict(cls, d):
        materials = {}
        for id_, m in d['materials'].items():
            material = Material.from_dict(m)
            materials[id_] = material

        shapes = {}
        for id_, s in d['shapes'].items():
            shape = [Vec.from_dict(v) for v in s]
            shapes[id_] = shape

        entities = {}
        for id_, e in d['entities'].items():
            entity = Collider.from_dict(e, id_, shapes, materials)
            entities[id_] = entity

        springs = []
        for s in d['springs']:
            spring = Spring.from_dict(s, entities)
            springs.append(spring)

        world = cls(gravity=Vec.from_dict(d['gravity']))
        world.add_ent(*entities.values())
        world.add_spring(*springs)

        return world
