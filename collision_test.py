import random

import pyglet

from base import *
from collision import *


def get_support(n, poly):
    return max(poly, key=lambda v: v.dot(n))


def get_separation(p1, p2):
    biggest_d = float('-inf')
    normal = Vec(0, 0)
    for i in range(len(p1)):
        # Find this edge.
        j = (i + 1) % len(p1)
        edge = p1[i] - p1[j]
        n = Vec(x=-edge.y, y=edge.x)
        n = n / abs(n)     # Normalise n.

        # Find support point of p2 along -n.
        s = get_support(-n, p2)
        # Find distance of support point from edge.
        d = n.dot(s - p1[i])

        # Keep track of deepest support point.
        if d > biggest_d:
            biggest_d = d
            normal = n

    return  biggest_d, normal


def collide(p1, p2):
    sep1 = get_separation(p1, p2) 
    sep2 = get_separation(p2, p1) 

    if sep1[0] > sep2[0]:
        return sep1
    else:
        # Invert normal so that it always points away from p1 and
        # towards p2.
        return (sep2[0], -sep2[1])


def collide_point(s, p1):
    biggest_d = float('-inf')
    for i in range(len(p1)):
        j = (i + 1) % len(p1)
        side = p1[i] - p1[j]
        n = Vec(x=-side.y, y=side.x)

        d = n.dot(s - p1[i])

        if d > biggest_d:
            biggest_d = d

    return biggest_d


#def collide_along(direction, polygon1, polygon2):
    #if isinstance(polygon1, Polygon):
        #polygon1 = polygon1.vertices
    #if isinstance(polygon2, Polygon):
        #polygon2 = polygon2.vertices
#
    ## Calculate support points.
    #p1_min, p1_max = min_max(map(lambda vert: (direction.dot(vert), vert),
                                 #polygon1),
                             #key=lambda t: t[0])
    #p2_min, p2_max = min_max(map(lambda vert: (direction.dot(vert), vert),
                                 #polygon2),
                             #key=lambda t: t[0])
#
#
    #if p1_min[0] > p2_max[0] or p1_max[0] < p2_min[0]:
        ## They are not touching.
        #return None
    #else:
        ## They are intersecting.
        ##return max(p1_min[0], 
        #return True
#
#
#def collide(polygon1, polygon2):
    ## Work out which axes need to be tested against.
    #test_axes = []
    #for polygon in (polygon1.vertices, polygon2.vertices):
        #for v1, v2 in zip(polygon, polygon[1:]):
            #side = v2 - v1
            #normal = Vec(x=-side.y, y=side.x)
            #test_axes.append(normal)
        #side = polygon[-1] - polygon[0]
        #normal = Vec(x=side.y, y=-side.x)
        #test_axes.append(normal)
#
    ## Test the polygons against the determined axes.
    #return all(map(lambda d: collide_along(d, polygon1.vertices, polygon2.vertices), test_axes))
#
#
#class Polygon:
    #def __init__(self, vertices, colour=(255, 255, 255)):
        #self.vertices = list(vertices)
        #self.colour = colour
#
    #def __iter__(self):
        #return iter((self.vertices, self.colour))


class Window(pyglet.window.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selection = None
        self.mouse = 0, 0

        self.shapes = [Poly(colour=(255, 0, 0),
                            vertices=[Vec(0, 0),
                                      Vec(1, 0),
                                      Vec(0, 1)]),
                       Poly(colour=(0, 255, 0),
                            vertices=[Vec(0, 0),
                                      Vec(1, 0),
                                      Vec(1, 1),
                                      Vec(0, 1)]),
                            #]
                       Poly(colour=(0, 0, 255),
                            vertices=[Vec(0.0, 0.0),
                                      Vec(1.0, 0.0),
                                      Vec(1.5, 0.5),
                                      Vec(0.5, 1.0),
                                      Vec(-.5, 0.5)])]
        for shape in self.shapes:
            for vertex in shape.vertices:
                vertex.x = vertex.x*100 + 100 + random.random()
                vertex.y = vertex.y*100 + 100 + random.random()

        print(self.shapes)

    def on_draw(self):
        try:
            self.on_draw_()
        except Exception as e:
            #assert False
            print(e)
            raise e

    def on_draw_(self):
        self.clear()
        messages = []

        # Collide shapes.
        def collide_all(shapes):
            if len(shapes) <= 1:
                return

            for shape in shapes[1:]:
                separation, axis = collide(shape.vertices, shapes[0].vertices)
                if separation < 0:
                    messages.append('Collision!')
                    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                            ('v2f', [self.mouse[0],
                                     self.mouse[1],
                                     self.mouse[0] + 100*axis.x,
                                     self.mouse[1] + 100*axis.y]
                            ))

            return collide_all(shapes[1:])
        collide_all(self.shapes)

        # Draw shapes.
        for p, c in self.shapes:
            L = len(p)
            vl = pyglet.graphics.vertex_list(L, ('v2f', tuple(flatten(p))),
                                                ('c3B', c * L))
            vl.draw(pyglet.gl.GL_POLYGON)

        # Draw message.
        for i, message in enumerate(messages):
            pyglet.text.Label(str(message),
                              font_name='Sans',
                              font_size=24,
                              y=self.height - i * 30,
                              anchor_y='top').draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse = x, y

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
        # elif symbol == pyglet.window.key._3:
        #     self.selection = 2
        else:
            super().on_key_press(symbol, modifiers)

window = Window(resizable=True)
pyglet.app.run()
