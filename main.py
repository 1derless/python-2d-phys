#!./venv/bin/python3

import time

import pyglet

from base import *


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse = (0, 0)
        self.line = (0, 0, 100, 100)
        self.rect = Rect(x=250, y=250, w=100, h=200)
        
        pyglet.clock.schedule(self.periodic_update)

    def periodic_update(self, dt):
        self.rect.t += dt

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.mouse = (x, y)

    def on_draw(self):
        window.clear()
        rect_vertices = self.rect.get_vertices_flat()
        vertices = pyglet.graphics.vertex_list_indexed(
            4, (0, 1, 2, 0, 2, 3),
            ('v2f', rect_vertices),
        )
        vertices.draw(pyglet.gl.GL_TRIANGLES)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f',
            (self.mouse[0], self.mouse[1], rect_vertices[0], rect_vertices[1]))
        )

        print(pyglet.clock.get_fps(), end="\r")


if __name__ == '__main__':
    window = Window(resizable=True, vsync=False)
    pyglet.app.run()
