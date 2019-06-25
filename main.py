#!./venv/bin/python3

import time

import pyglet

from base import *


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse = (0, 0)
        self.rect = Rect(x=250, y=250, w=100, h=200)

        self.proj = Projectile(pos=Vec(300, 300), mass=1)
        self.phys_world = PhysWorld()
        self.phys_world.gravity.y = -50
        self.phys_world.add_obj(self.proj)
        
        pyglet.clock.schedule_interval(self.periodic_update, 1/120)

    def periodic_update(self, dt):
        self.rect.angle += dt
        self.rect.x, self.rect.y = tuple(self.proj.pos)

        self.phys_world.update(dt)

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.mouse = (x, y)
        self.phys_world.s_pos = Vec(*self.mouse)

    def on_draw(self):
        self.clear()
        rect_vertices = self.rect.get_vertices_flat()
        vertices = pyglet.graphics.vertex_list_indexed(
            4, (0, 1, 2, 0, 2, 3),
            ('v2f', rect_vertices),
        )
        vertices.draw(pyglet.gl.GL_TRIANGLES)

        # Draw line from origin to centre of rectangle.
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
            ('v2f', (self.mouse[0], self.mouse[1],
            (rect_vertices[0] + rect_vertices[4]) / 2,
            (rect_vertices[1] + rect_vertices[5]) / 2))
        )

        print(pyglet.clock.get_fps(), end="      \r")


if __name__ == '__main__':
    window = Window(resizable=True, vsync=True)
    pyglet.app.run()
