""" Basic datatypes and functions
This module provides the basic datatypes for the physics engine and
some utility functions.
"""

import itertools
from math import sin, cos

__all__ = ['take', 'flatten', 'min_max', 'Vec', 'Rect', 'Poly']


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


def min_max(iterable):
    """Find the minimum and maximum of a single iterable."""
    iterable = iter(iterable)
    try:
        min_ = max_ = next(iterable)
    except StopIteration:
        raise ValueError("min_max() arg is an empty sequence")

    for item in iterable:
        if min_ > item:
            min_ = item

        if max_ < item:
            max_ = item

    return min_, max_


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

    def __itruediv__(self, other: float):
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

    def __abs__(self):
        return (self.x**2 + self.y**2) ** 0.5

    def cross(self, other):
        """Compute mathematical cross product and return it."""
        return self.x * other.y - self.y * other.x

    def dot(self, other):
        """Compute mathematical dot product and return it."""
        return self.x * other.x + self.y * other.y

    def rotate(self, t):
        """Rotate by `t` radians anticlockwise around (0, 0)."""
        return Vec(x=self.x*cos(t) - self.y*sin(t),
                   y=self.x*sin(t) + self.y*cos(t))

    def rotate_inplace(self, t):
        """Rotate by `t` radians anticlockwise around (0, 0) inplace."""
        self.x, self.y = (self.x*cos(t) - self.y*sin(t),
                          self.x*sin(t) + self.y*cos(t))


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0, angle=0, colour=(255, 255, 255)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.angle = angle
        self.colour = colour

    def get_vertices(self):
        """Returns positions of all 4 corners."""
        w = self.w / 2
        h = self.h / 2
        vertices = (Vec(-w, -h),
                    Vec( w, -h),
                    Vec( w,  h),
                    Vec(-w,  h))

        for vertex in vertices:
            vertex.rotate_inplace(self.angle)
            vertex += Vec(self.x, self.y)  # translate

        return vertices

    def get_vertices_flat(self):
        """Returns all 4 corners's positions in a flat tuple."""
        return tuple(flatten(self.get_vertices()))

    def get_poly(self):
        return Poly(vertices=self.get_vertices(), colour=self.colour)


class Poly:
    def __init__(self, vertices, colour=(255, 255, 255)):
        self.vertices = list(vertices)
        self.colour = colour

    def __iter__(self):
        return iter((self.vertices, self.colour))
