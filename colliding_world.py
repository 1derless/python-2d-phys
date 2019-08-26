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
        bounce = 100
        def callback(o1, o2, separation, axis):
            force = bounce * -separation * axis
            o1.new_acc -= force / o1.mass
            o2.new_acc += force / o2.mass

            # Find a point in space to apply the torque from.
            pos = get_intersector(o1.get_vertices(), o2.get_vertices(), axis)

            # Calculate torque.
            normal = Vec(x=-force.y, y=force.x)
            torque = pos.cross(normal) / bounce
            o1.new_ang_acc += torque / o1.moi
            o2.new_ang_acc -= torque / o2.moi

        collide_all(self._objects, callback)
        return
        separation, axis = collide(
            self._objects[0].get_vertices(),
            self._objects[2].get_vertices(),
            )

        if separation < 0.0:
            callback(
                self._objects[0],
                self._objects[2],
                separation,
                axis,
                )
