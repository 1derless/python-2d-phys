import random

import pyglet

from base import *
from collision import *


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
                            ]
                       #Poly(colour=(0, 0, 255),
                       #     vertices=[Vec(0.0, 0.0),
                       #               Vec(1.0, 0.0),
                       #               Vec(1.5, 0.5),
                       #               Vec(0.5, 1.0),
                       #               Vec(-.5, 0.5)])]
        for shape in self.shapes:
            for vertex in shape.vertices:
                vertex.x = vertex.x*100 + 100
                vertex.y = vertex.y*100 + 100

        print(self.shapes)

    def on_draw(self):
        try:
            self.on_draw_()
        except Exception as e:
            import traceback
            traceback.print_exc(e)
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
                if collide(shape, shapes[0]) is not None:
                    a = collide(shape, shapes[0])
                    messages.append('Collision!')
                    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                            ('v2f', [self.mouse[0],
                                     self.mouse[1],
                                     self.mouse[0] + a.x,
                                     self.mouse[1] + a.y]
                            ))

            return collide_all(shapes[1:])
        #collide_all(self.shapes)

        # Draw shapes.
        for p, c in self.shapes:
            L = len(p)
            vl = pyglet.graphics.vertex_list(L, ('v2f', tuple(flatten(p))),
                                                ('c3B', c * L))
            vl.draw(pyglet.gl.GL_POLYGON)

        #def new_collide(p1, p2):
        #    biggest_d = float('-inf')
        #    for i in range(len(p1)):
        #        n = p1[i] - p1[(i + 1) % len(p1)]
        #        #n = Vec(x=-1, y=0)
        #        #s = max(map(lambda v: ((-n).dot(v), v),
        #        s = min(map(lambda v: (v.dot(n), v),
        #                    p2),
        #                key=lambda t: t[0])[1]
        #        d = n.dot(s - p1[i])

        #        if d > biggest_d:
        #            biggest_d = d

        #    #print(biggest_d)

        def new_collide(s, p1):
            biggest_d = float('-inf')
            for i in range(len(p1)):
                j = (i + 1) % len(p1)
                side = p1[i] - p1[j]
                n = Vec(x=-side.y, y=side.x)
                #n = Vec(x=-1, y=0)
                #s = max(map(lambda v: ((-n).dot(v), v),
                #s = min(map(lambda v: (v.dot(n), v),
                #            p2),
                #        key=lambda t: t[0])[1]
                d = n.dot(s - p1[i])

                if d > biggest_d:
                    biggest_d = d

            return biggest_d

        if self.selection is not None:
            from itertools import product

            #points = filter(lambda t: new_collide(Vec(*t), self.shapes[self.selection].vertices) > 0,
            #                product(range(self.width), range(self.height)))
            #points = list(flatten(points))
            #pyglet.graphics.draw(len(points) // 2, pyglet.gl.GL_POINTS, ('v2f', points))

            points = list(flatten(product(range(self.width), range(self.height))))

            colours = list(map(lambda t: new_collide(Vec(*t), self.shapes[self.selection].vertices),
                               product(range(self.width), range(self.height))))

            min_ = min(colours)
            max_ = max(colours)
            #colours = [(0, int(c * 255 / min_), 0) if c < 0 else (0, 0, int(c * 255 / max_)) for c in colours]

            colours = list(map(lambda c: (int((c - min_) / max_ * 255), ) * 3, colours))
            pyglet.graphics.draw(len(points) // 2, pyglet.gl.GL_POINTS,
                    ('v2f', points),
                    ('c3B', list(flatten(colours))))


        #if new_collide(self.shapes[0].vertices, self.shapes[1].vertices):
            #/ 2**1/2
        #    pass

        # Draw message.
        pyglet.text.Label('    '.join(messages),
                          font_name='Sans',
                          font_size=24,
                          y=self.height,
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
        elif symbol == pyglet.window.key._3:
            self.selection = 2
        else:
            super().on_key_press(symbol, modifiers)

window = Window(resizable=True)
pyglet.app.run()
