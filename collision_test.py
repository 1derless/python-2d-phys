import random

import pyglet

from base import *
from collision import *


def collide_along(direction, polygon1, polygon2):
    if isinstance(polygon1, Polygon):
        polygon1 = polygon1.vertices
    if isinstance(polygon2, Polygon):
        polygon2 = polygon2.vertices

    # Calculate support points.
    polygon1_projected = map(lambda vertex: direction.dot(vertex), polygon1)
    polygon2_projected = map(lambda vertex: direction.dot(vertex), polygon2)
    p1_min, p1_max = min_max(polygon1_projected)
    p2_min, p2_max = min_max(polygon2_projected)

    if p1_min > p2_max or p1_max < p2_min:
        # They are not touching.
        return False
    else:
        # They are intersecting.
        return True

def collide(polygon1, polygon2):
    # Work out which axes need to be tested against.
    test_axes = []
    for polygon in (polygon1.vertices, polygon2.vertices):
        for v1, v2 in zip(polygon, polygon[1:]):
            side = v2 - v1
            normal = Vec(x=-side.y, y=side.x)
            test_axes.append(normal)
        side = polygon[-1] - polygon[0]
        normal = Vec(x=side.y, y=-side.x)
        test_axes.append(normal)

    # Test the polygons against the determined axes.
    return all(map(lambda d: collide_along(d, polygon1.vertices, polygon2.vertices), test_axes))


class Polygon:
    def __init__(self, vertices, colour=(255, 255, 255)):
        self.vertices = list(vertices)
        random.shuffle(self.vertices)
        self.colour = colour

    def __iter__(self):
        return iter((self.vertices, self.colour))


class Window(pyglet.window.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.axis = Vec(x=1, y=0)
        self.control_vertex = False
        self.control_normal = False

        self.poly1 = Polygon(colour=(255, 0, 0),
                             vertices=[Vec(0, 0),
                                       Vec(0, 1),
                                       #Vec(1, 1),
                                       Vec(1, 0)])

        self.poly2 = Polygon(colour=(0, 255, 0),
                             vertices=[Vec(1, 2),
                                       Vec(2, 2),
                                       Vec(2, 1),
                                       Vec(1, 1)])

    def on_draw(self):
        self.clear()
        x = 100
        y = 100
        sx = 100
        sy = 100

        for p, c in (self.poly1, self.poly2):
            L = len(p)
            verts = list(flatten(map(lambda v: (v[0]*sx + x, v[1]*sy + y), p)))
            vl = pyglet.graphics.vertex_list(L, ('v2f', verts),
                                                ('c3B', c * L))
            vl.draw(pyglet.gl.GL_POLYGON)

        if collide_along(self.axis, self.poly1, self.poly2):
            pyglet.graphics.vertex_list(3, ('v2f', [0, 50, 50, 50, 50, 0]),
                                           ('c3B', [255, 0, 255] * 3)
                                       ).draw(pyglet.gl.GL_TRIANGLES)

        if collide(self.poly1, self.poly2):
            pyglet.graphics.vertex_list(3, ('v2f', [0, 0, 0, 50, 50, 0]),
                                           ('c3B', [0, 255, 255] * 3)
                                       ).draw(pyglet.gl.GL_TRIANGLES)

        # draw axis
        pyglet.graphics.vertex_list(
                2,
                ('v2f', [100, 100, self.axis.x*sx + x, self.axis.y*sy + y]),
                ('c3B', [0, 0, 255] * 2)
                ).draw(pyglet.gl.GL_LINES)

    def on_mouse_motion(self, x, y, dx_, dy_):
        if self.control_vertex:
            self.poly2.vertices[2] = Vec(x=(x - 100) / 100, y=(y - 100) / 100)
        
        if self.control_normal:
            self.axis = Vec(y=-(x - 100) / 100, x=(y - 100) / 100)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.S:
            self.axis = Vec(x=float(input('X:')), y=float(input('Y:')))

        elif symbol == pyglet.window.key.M:
            self.control_vertex = not self.control_vertex

        elif symbol == pyglet.window.key.N:
            self.control_normal = not self.control_normal

        elif symbol == pyglet.window.key.L:
            self.axis = poly2[2] - poly2[0]
            self.axis.x, self.axis.y = self.axis.y, -self.axis.x

        elif symbol == pyglet.window.key.P:
            print(poly2[2], poly2[1] - poly2[2])

        elif symbol == pyglet.window.key.F:
            self.axis = Vec() - self.axis

        elif symbol == pyglet.window.key.Y:
            polygon1_projected = map(lambda vertex: self.axis.dot(vertex), poly1)
            polygon2_projected = map(lambda vertex: self.axis.dot(vertex), poly2)
            p1_min, p1_max = min_max(polygon1_projected)
            p2_min, p2_max = min_max(polygon2_projected)
            print(p1_min, p1_max, p2_min, p2_max)

        else:
            super().on_key_press(symbol, modifiers)

window = Window(resizable=True)
pyglet.app.run()
#print(
#collide(Polygon([Vec(0, 0), Vec(1, 0), Vec(0, 1)]),
#        Polygon([Vec(2, 2), Vec(3, 2), Vec(2, 3)]))
#        )
