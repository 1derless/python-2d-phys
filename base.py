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
        self._springs = []
        self.gravity = Vec(0, 0)
        self.s_pos = Vec(0, 0)

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
