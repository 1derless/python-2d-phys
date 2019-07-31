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
        self.colour = colour

    def __iter__(self):
        return iter((self.vertices, self.colour))


class Window(pyglet.window.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selection = None

        self.shapes = [Polygon(colour=(255, 0, 0),
                               vertices=[Vec(0, 0),
                                         Vec(1, 0),
                                         Vec(0, 1)]),
                       Polygon(colour=(0, 255, 0),
                               vertices=[Vec(0, 0),
                                         Vec(1, 0),
                                         Vec(1, 1),
                                         Vec(0, 1)]),
                       Polygon(colour=(0, 0, 255),
                               vertices=[Vec(0.0, 0.0),
                                         Vec(1.0, 0.0),
                                         Vec(1.5, 0.5),
                                         Vec(0.5, 1.0),
                                         Vec(-.5, 0.5)])]
        for shape in self.shapes:
            for vertex in shape.vertices:
                vertex.x = vertex.x*100 + 100
                vertex.y = vertex.y*100 + 100

        print(self.shapes)

    def on_draw(self):
        self.clear()
        messages = []

        # Collide shapes.
        def collide_all(shapes):
            if len(shapes) <= 1:
                return

            for shape in shapes[1:]:
                if collide(shape, shapes[0]):
                    messages.append('Collision!')

            return collide_all(shapes[1:])
        collide_all(self.shapes)

        # Draw shapes.
        for p, c in self.shapes:
            L = len(p)
            vl = pyglet.graphics.vertex_list(L, ('v2f', tuple(flatten(p))),
                                                ('c3B', c * L))
            vl.draw(pyglet.gl.GL_POLYGON)

        # Draw message.
        pyglet.text.Label('    '.join(messages),
                          font_name='Sans',
                          font_size=24,
                          y=self.height,
                          anchor_y='top').draw()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.selection is not None:
            for vertex in self.shapes[self.selection].vertices:
                vertex.x += dx
                vertex.y += dy

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key._0:
            self.selection = None
        elif symbol == pyglet.window.key._1:
            self.selection = 0
        elif symbol == pyglet.window.key._2:
            self.selection = 1
        elif symbol == pyglet.window.key._3:
            self.selection = 2
        else:
            super().on_key_press(symbol, modifiers)

window = Window(resizable=True)
pyglet.app.run()
