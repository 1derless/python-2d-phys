from base import *
from collision import *
from phys import *

__all__ = ['CollidingWorld']


class CollidingWorld(PhysWorld):
    def add_obj(self, *objs):
        for obj in objs:
            if not isinstance(obj, Collider):
                raise TypeError(f"{obj} is not a Collider")

            super().add_obj(obj)

    def update(self, dt):
        self.dampen(dt / 10)
        self.update_spring(dt)
        self.update_collision(dt)
        self.update_turn(dt)
        self.update_move(dt)

    def update_collision(self, dt):
        bounce = 50.0
        def callback(o1, o2, separation, axis):
            n = axis  #Vec(x=-axis.y, y=axis.x)
            dv = o2.vel - o1.vel

            v_dot_n = dv.dot(n)

            if v_dot_n > 0.0:
                return

            # Find a point in space to apply the torque from.
            pos = get_intersector(o1.get_vertices(), o2.get_vertices(), axis)
            # .. on o1
            pos_o1 = pos - o1.pos
            # .. on o2
            pos_o2 = pos - o2.pos

            # Calculate scalar impulse.
            e = 0.75   # coeff. of restitution
            j = -(1 + e) * v_dot_n
            j /= 1/o1.mass + 1/o2.mass \
                 + (abs(pos_o1) * dt)**2 / o2.moi \
                 + (abs(pos_o2) * dt)**2 / o2.moi

            # Apply impulse
            # This ignores the velocity Verlet because collisions do not
            # apply steady or smooth forces.
            impulse = j * n
            o1.vel -= 1/o1.mass * impulse
            o2.vel += 1/o2.mass * impulse

            # Calculate torque.
            normal = Vec(x=-impulse.y, y=impulse.x)
            torque1 = pos_o1.cross(n)
            torque2 = pos_o2.cross(n)
            o1.ang_vel -= torque1 / o1.moi
            o2.ang_vel += torque2 / o2.moi
            o1.ang_vel = max(min(o1.ang_vel, 1), -1)
            o2.ang_vel = max(min(o2.ang_vel, 1), -1)
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

        collide_all(self._objects, callback)
