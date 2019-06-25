#!./venv/bin/python3

import time

import pyglet

from base import *


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse = (0, 0)
        self.rect = Rect(x=250, y=250, w=100, h=200)

        self.p1 = Projectile(pos=Vec(700, 1000), mass=0.1)
        self.p1.vel.x -= 500
        self.p2 = Projectile(pos=Vec(750, 600), mass=0.5)
        self.p2.vel.x += 100

        self.pin = Pin(pos=Vec(700, 1000))

        self.s1 = Spring(stiffness=0.75, end1=self.p1, end2=self.p2)
        self.s2 = Spring(stiffness=0.5, end1=self.pin, end2=self.p2)

        self.phys_world = PhysWorld()
        # self.phys_world.gravity.y = -75
        self.phys_world.add_obj(self.p1, self.p2)
        self.phys_world.add_spring(self.s1, self.s2)
        
        pyglet.clock.schedule_interval(self.periodic_update, 1/120)
        #pyglet.clock.schedule(self.periodic_update)

    def periodic_update(self, dt):
        self.rect.angle += dt
        #self.rect.x, self.rect.y = tuple(self.proj.pos)

        self.phys_world.update(dt)

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.mouse = (x, y)
        #self.s2.pos = Vec(x, y)

    def on_draw(self):
        self.clear()
        #rect_vertices = self.rect.get_vertices_flat()
        #vertices = pyglet.graphics.vertex_list_indexed(
        #    4, (0, 1, 2, 0, 2, 3),
        #    ('v2f', rect_vertices),
        #)
        #vertices.draw(pyglet.gl.GL_TRIANGLES)

        for p in (self.p1, self.p2):
            spot = pyglet.graphics.vertex_list_indexed(
                4, (0, 1, 2, 0, 2, 3),
                ('v2f', (          p.pos.x, p.pos.y - 50*p.mass,
                         -50*p.mass + p.pos.x, p.pos.y,
                                   p.pos.x, p.pos.y + 50*p.mass ,
                          50*p.mass + p.pos.x, p.pos.y))
            )
            spot.draw(pyglet.gl.GL_TRIANGLES)

        # Draw springs.
        for s in (self.s1, self.s2):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2f',
                    (s.end1.pos.x, s.end1.pos.y, s.end2.pos.x, s.end2.pos.y))
            )


        print(pyglet.clock.get_fps(), end="      \r")


if __name__ == '__main__':
    window = Window(resizable=True, vsync=True)
    pyglet.app.run()
