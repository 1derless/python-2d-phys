from base import *
from collision import *
from phys import *

__all__ = ['CollidingWorld']


class CollidingWorld(System):
    def add_ent(self, *objs):
        for obj in objs:
            if not isinstance(obj, Collider):
                raise TypeError(f"{obj} is not a Collider")

            super().add_ent(obj)

    def update(self, dt):
        self.dampen(dt)
        self.update_spring(dt)
        self.update_collision(dt)
        self.update_turn(dt)
        self.update_move(dt)

    def update_collision(self, dt):

        def callback(o1, o2, separation, axis):
            if o1.mass == float('inf') and o2.mass == float('inf'):
                return

            n = axis  #Vec(x=-axis.y, y=axis.x)
            dv = o2.vel - o1.vel

            v_dot_n = dv.dot(n)

            if v_dot_n > 0.0:
                # If the two objects are moving away from each other,
                # then they are already going out of collision.
                return

            # Find a point in space to apply the torque from on each object.
            pos = get_intersector(o1.get_vertices(), o2.get_vertices(), axis)
            if pos is None:
                return
            pos_o1 = pos - o1.pos
            pos_o2 = pos - o2.pos

            # Calculate scalar impulse.
            e = 0.5  # coeff. of restitution
            j = -(1 + e) * v_dot_n
            j /= 1/o1.mass + 1/o2.mass \
                + (abs(pos_o1) * dt)**2 / o1.moi \
                + (abs(pos_o2) * dt)**2 / o2.moi

            # Apply impulse.
            # This ignores the velocity Verlet because collisions do not
            # apply steady or smooth forces.
            impulse = j * n
            o1.vel -= 1/o1.mass * impulse
            o2.vel += 1/o2.mass * impulse

            # Calculate and apply torque.
            torque1 = pos_o1.cross(impulse)
            torque2 = pos_o2.cross(impulse)
            o1.ang_vel -= torque1 * e / o1.moi
            o2.ang_vel += torque2 * e / o2.moi
            #o1.ang_vel = max(min(o1.ang_vel, 1), -1)
            #o2.ang_vel = max(min(o2.ang_vel, 1), -1)


            # Correct position for rounding errors.
            if separation < -1:
                correction = (-separation - 1) / (1/o1.mass + 1/o2.mass) * 0.01 * n
                #o1.vel = max(1 / o1.mass * correction * dt, o1.vel, key=abs)
                #o2.vel = max(1 / o2.mass * correction * dt, o2.vel, key=abs)
                o1.pos -= 1 / o1.mass * correction
                o2.pos += 1 / o2.mass * correction
                #force = -separation * axis
                #o1.new_acc -= force / o1.mass
                #o2.new_acc += force / o2.mass

            # Calculate and apply friction.
            mu = 0.75

            dv = o2.vel - o1.vel  # Update as dv should have changed.
            t = dv - n * dv.dot(n)
            #print(dv, n, dv.dot(n), n * dv.dot(n), t, abs(t))
            if abs(t) == 0:
                return
            t /= abs(t)

            jt = -dv.dot(t)
            jt /= 1/o1.mass + 1/o2.mass

            if abs(jt) < j * mu:
                # Object is nearly at rest, apply static friction.
                impulse = jt * t
            else:
                # Object is not nearly at rest, apply dynamic friction.
                impulse = -j * t * 0.25
                print(impulse)

            o1.vel -= 1/o1.mass * impulse
            o2.vel += 1/o2.mass * impulse

            '''
            return

            force = bounce * -separation * axis
            o1.new_acc -= force / o1.mass
            o2.new_acc += force / o2.mass

            # Find a point in space to apply the torque from.
            pos = get_intersector(o1.get_vertices(), o2.get_vertices(), axis)

            # Calculate torque.
            force /= bounce
            normal = Vec(x=-force.y, y=force.x)
            torque1 = (pos - o1.pos).cross(n)
            torque2 = (pos - o2.pos).cross(n)
            o1.ang_vel -= torque1 / o1.moi
            o2.ang_vel += torque2 / o2.moi

            return
            # Calculate torque.
            normal = Vec(x=-force.y, y=force.x)
            torque = pos.cross(normal) / bounce
            o1.new_ang_acc += torque / o1.moi
            normal = Vec(x=force.y, y=-force.x)
            torque = pos.cross(normal) / bounce
            o2.new_ang_acc -= torque / o2.moi
            '''

        collide_all(self._entities, callback)
