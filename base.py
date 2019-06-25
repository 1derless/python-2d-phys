""" Basic datatypes and functions
This module provides the basic datatypes for the physics engine and
some utility functions.
"""

import itertools
from math import sin, cos

#__all__ = ['take', 'flatten', 'Vec', 'Rect']


def take(n, iterable):
    """Yield from `iterable` in batches of length `n`.

    It stops when `iterable` has fewer than `n` elements remaining.
    """
    i = iter(iterable)

    while True:
        yield tuple((next(i) for _ in range(n)))


def flatten(iterable):
    """Flatten an iterable of iterables."""
    return itertools.chain.from_iterable(iterable)


class Vec:
    # Restrict instances to hold only the attributes in the following
    # table.  This saves memory at the cost of flexibility.
    __slots__ = ["x", "y"]

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f"Vec(x={self.x}, y={self.y})"

    def __add__(self, other):
        return Vec(x=self.x + other.x,
                   y=self.y + other.y)
    __radd__ = __add__

    def __sub__(self, other):
        return Vec(x=self.x - other.x,
                   y=self.y - other.y)

    def __mul__(self, other):
        return Vec(x=self.x * other,
                   y=self.y * other)
    __rmul__ = __mul__

    def __truediv__(self, other):
        return Vec(x=self.x / other,
                   y=self.y / other)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, other: float):
        self.x *= other
        self.y *= other
        return self

    def __idiv__(self, other: float):
        self.x /= other
        self.y /= other
        return self

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise IndexError

    def rotate(self, t):
        """Rotate by `t` radians anticlockwise around (0, 0)."""
        self.x, self.y = (self.x*cos(t) - self.y*sin(t),
                          self.x*sin(t) + self.y*cos(t))


class PhysObj:
    """A basic physics object."""
    ...


class PhysWorld:
    def __init__(self):
        self._objects = []
        self.gravity = Vec(0, 0)
        self.s_pos = Vec(0, 0)

    def add_obj(self, *objs):
        for obj in objs:
            if not isinstance(obj, PhysObj):
                raise TypeError(f"{obj} is not a PhysObj")

            self._objects.append(obj)

    def update(self, dt):
        for obj in self._objects:
            # Calculate new position using Velocty Verlet

            # Springs
            stiffness = 0.75
            new_acc = (self.s_pos - obj.pos) * (stiffness / obj.mass)

            # Apply gravity.
            new_acc += self.gravity

            # Move object.
            obj.pos += obj.vel*dt + new_acc*dt*dt/2.0
            obj.vel += (obj.acc + new_acc) * dt / 2.0
            obj.acc = new_acc


class Pin(PhysObj):
    """A fixed point in space."""
    @property
    def vel(self):
        return Vec(0, 0)

    # @vel.setter
    # def vel(self, value):
    #     pass

    def __init__(self, pos):
        self.pos = pos


class Projectile(PhysObj):
    def __init__(self, pos, mass):
        self.pos = pos
        self.mass = mass
        self.vel = Vec(x=0, y=0)
        self.acc = Vec(x=0, y=0)


class Spring:
    def update(self):
        ...


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0, angle=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.angle = angle

    def get_vertices(self):
        """Returns positions of all 4 corners."""
        w = self.w / 2
        h = self.h / 2
        vertices = (Vec(-w, -h),
                    Vec( w, -h),
                    Vec( w,  h),
                    Vec(-w,  h))

        for vertex in vertices:
            vertex.rotate(self.angle)
            vertex += Vec(self.x, self.y)  # translate

        return vertices

    def get_vertices_flat(self):
        """Returns all 4 corners's positions in a flat tuple."""
        return tuple(flatten(self.get_vertices()))
