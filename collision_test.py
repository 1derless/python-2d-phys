import random

import pyglet

from base import *
from collision import *


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

    def on_draw(self):
        try:
            self.on_draw_()
        except Exception as e:
            assert False
            print(e)
            raise e

    def on_draw_(self):
        self.clear()
        messages = []

        messages.append('Sq & mouse: {}'.format(
                            collide_point(Vec(*self.mouse),
                                          self.shapes[1].vertices)))

        # Draw shapes.
        for p, c in self.shapes:
            L = len(p)
            vl = pyglet.graphics.vertex_list(L, ('v2f', tuple(flatten(p))),
                                                ('c3B', c * L))
            vl.draw(pyglet.gl.GL_POLYGON)

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

                    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                            ('v2f', tuple(
                                get_intersector(
                            shape.vertices,
                            shapes[0].vertices,
                            axis))))

            return collide_all(shapes[1:])
        collide_all(self.shapes)

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
