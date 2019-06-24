""" Basic datatypes and functions
This module provides the basic datatypes for the physics engine and
some utility functions.
"""

import itertools
from math import sin, cos

__all__ = ['take', 'flatten', 'Vec', 'Rect']


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

    def __mul__(self, other: float):
        return Vec(x=self.x * other,
                   y=self.y * other)

    def __iadd__(self, other):
        self.x = self.x + other.x
        self.y = self.y + other.y

    def __imul__(self, other: float):
        self.x *= other
        self.y *= other

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


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0, t=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.t = t

    def get_vertices(self):
        """Returns positions of all 4 corners."""
        w = self.w / 2
        h = self.h / 2
        vertices = (Vec(-w, -h),
                    Vec( w, -h),
                    Vec( w,  h),
                    Vec(-w,  h))

        for vertex in vertices:
            vertex.rotate(self.t)
            vertex += Vec(self.x, self.y)  # translate

        return vertices

    def get_vertices_flat(self):
        """Returns all 4 corners's positions in a flat tuple."""
        return tuple(flatten(self.get_vertices()))
