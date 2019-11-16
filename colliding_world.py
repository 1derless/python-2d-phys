from base import *
from collision import *
from phys import *

__all__ = ['CollidingWorld']


class CollidingWorld(System):
    imps = []
    def add_ent(self, *objs):
        for obj in objs:
            if not isinstance(obj, Collider):
                raise TypeError(f"{obj} is not a Collider")

            super().add_ent(obj)

    def update(self, dt):
        #import random; random.shuffle(self._entities)
        self.dampen(dt)
        self.update_spring(dt)
        self.imps = [imp[:3] + [imp[3] - 1] for imp in self.imps if imp[3] > 0]
        self.update_collision(dt)
        self.update_turn(dt)
        self.update_move(dt)

    def update_collision(self, dt):
        def apply_impulse(entity, impulse, collision_normal):
            entity.new_vel += impulse / entity.mass
            entity.new_ang_vel += collision_normal.cross(impulse) / entity.moi

            if entity.mass != float('inf'):
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
                #force = -separation * axis
                #o1.new_acc -= force / o1.mass
                #o2.new_acc += force / o2.mass

        def resolve(o1, o2, separation, axis):
            if o1.mass == float('inf') and o2.mass == float('inf'):
                return

            # Find a point in space to apply the torque from on each object.
            pos = get_intersector(o1.get_vertices(), o2.get_vertices(), axis)
            if pos is None:
                return
            pos_o1 = pos - o1.pos
            pos_o2 = pos - o2.pos

            n = axis  #Vec(x=-axis.y, y=axis.x)
            #dv = o2.vel + o2.ang_vel * pos_o2 - (
            #     o1.vel + o1.ang_vel * pos_o1)
            dv = o2.vel - o1.vel

            v_dot_n = dv.dot(n)

            if v_dot_n > 0.0:
                # If the two objects are moving away from each other,
                # then they are already going out of collision.
                return

            # Calculate scalar impulse, j.
            e = 0.2  # coeff. of restitution
            j = -(1 + e) * v_dot_n
            j /= 1/o1.mass + 1/o2.mass \
                + (abs(pos_o1) * dt)**2 / o1.moi \
                + (abs(pos_o2) * dt)**2 / o2.moi

            # Apply impulse.
            # This ignores the velocity Verlet because collisions do not
            # apply steady or smooth forces.
            impulse = j * n
            apply_impulse(o1, -impulse, pos_o1)
            apply_impulse(o2, impulse, pos_o2)

            # Calculate and apply friction.
            mu = 0.4

            #dv = o2.new_vel - o1.new_vel  # Update as dv should have changed.
            dv = o2.new_vel + o2.new_ang_vel * pos_o2 - (
                 o1.new_vel + o1.new_ang_vel * pos_o1)
            t = dv - n * dv.dot(n)

            if abs(t) == 0:
                return
            t /= abs(t)

            jt = -dv.dot(t)  # Scalar impulse along tangent
            jt /= 1/o1.mass + 1/o2.mass

            if abs(jt) < j * mu:
                # Object is nearly at rest, apply static friction.
                impulse = jt * t
            else:
                # Object is not nearly at rest, apply dynamic friction.
                impulse = t * -j * 0.2

            #o1.new_vel += 1/o1.mass * -impulse
            #o2.new_vel += 1/o2.mass * impulse

            apply_impulse(o1, -impulse, pos_o1)
            apply_impulse(o2, impulse, pos_o2)

        collisions = collide_all(self._entities)
        for o1, o2, separation, normal in collisions:
            resolve(o1, o2, separation, normal)

        for o1, o2, separation, normal in collisions:
            correct_positions(o1, o2, separation, normal)

