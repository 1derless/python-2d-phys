"""Classes and functions for emulating 2D physics"""

from base import *


__all__ = ['PhysObj', 'PhysWorld', 'Pin', 'Projectile', 'Spring']


class PhysObj:
    """A basic physics object."""
    ...


class PhysWorld:
    def __init__(self):
        self._objects = []
        self._springs = []
        self.gravity = Vec(0, 0)

    def add_obj(self, *objs):
        for obj in objs:
            if not isinstance(obj, PhysObj):
                raise TypeError(f"{obj} is not a PhysObj")

            self._objects.append(obj)

    def add_spring(self, *springs):
        for spring in springs:
            if not isinstance(spring, Spring):
                raise TypeError(f"{spring} is not a Spring")

            self._springs.append(spring)

    def update(self, dt):
        for spring in self._springs:
            force = (spring.end2.pos - spring.end1.pos) * spring.stiffness
            spring.end1.new_acc += force / spring.end1.mass
            spring.end2.new_acc -= force / spring.end2.mass

        for obj in self._objects:
            # Apply gravity.
            obj.new_acc += self.gravity

            # Calculate new position using Velocty Verlet.
            obj.vel += (obj.acc + obj.new_acc) * dt / 2
            obj.acc = obj.new_acc
            obj.pos += obj.vel*dt + obj.new_acc*dt*dt/2
            obj.new_acc = Vec(x=0, y=0)


class Pin(PhysObj):
    """A fixed point in space."""
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        pass

    def __init__(self, pos):
        self._pos = pos
        self.vel = Vec()
        self.acc = Vec()
        self.new_acc = Vec()
        self.mass = float('inf')


class Projectile(PhysObj):
    def __init__(self, pos, mass):
        self.pos = pos
        self.mass = mass
        self.vel = Vec(x=0, y=0)
        self.acc = Vec(x=0, y=0)
        self.new_acc = Vec()


class Spring:
    def __init__(self, stiffness, end1, end2):
        self.stiffness = stiffness
        self.end1 = end1
        self.end2 = end2
