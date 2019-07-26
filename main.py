#!./venv/bin/python3

import time
import math
import gc

import pyglet
from pyglet.window import key

from base import *
from phys import *


class DrawableWorld(PhysWorld):
    def draw(self):
        for o in self._objects:
            # Draw objects:
            rect = Rect(x=o.pos.x, y=o.pos.y, w=200*o.mass, h=400*o.mass,
                        angle=o.ang)

            verts = pyglet.graphics.vertex_list_indexed(
                4, (0, 1, 2, 0, 2, 3),
                ('v2f', rect.get_vertices_flat())
            )
            verts.draw(pyglet.gl.GL_TRIANGLES)

        # Draw springs.
        for s in self._springs:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2f', tuple(s.get_end1_join_pos() + s.end1.pos)
                      + tuple(s.get_end2_join_pos() + s.end2.pos)
                )
            )


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse = (0, 0)
        self.rect = Rect(x=250, y=250, w=100, h=200)
        self.force_gc = False
        self.time = 0

        self.p = PhysObj(pos=Vec(x=500, y=450), mass=0.5, ang=0,
                           moi=0.5 * (100**2 + 200**2) / 12)
        point2 = PhysObj(pos=Vec(x=300, y=300), mass=0.1, ang=0,
                           moi=0.1 * (100**2 + 200**2) / 12)

        self.pin = Pin(pos=Vec(450, 400))
        self.mouse_pin = Pin(pos=Vec(450, 400))

        self.s = Spring(stiffness=0.99, end1=self.mouse_pin, end2=self.p,
                        slack_length=100, end2_join_pos=Vec(50, 100))

        spring1 = Spring(stiffness=0.75, end1=self.p, end2=point2,
                         end1_join_pos=Vec(-50, -100))
        spring2 = Spring(stiffness=0.45, end1=point2, end2=self.pin,
                         end1_join_pos=Vec(-10, 20))

        self.phys_world = DrawableWorld()
        self.phys_world.gravity.y = -9.81
        self.phys_world.add_obj(self.p, point2)
        self.phys_world.add_spring(self.s, spring1, spring2)
        
        pyglet.clock.schedule_interval(self.periodic_update, 1/120)
        #pyglet.clock.schedule(self.periodic_update)

    def periodic_update(self, dt):
        self.time += dt

        #self.mouse_pin.relocate(Vec(x=500 + 250*math.cos(self.time),
        #                            y=750 - 250*math.sin(self.time)))

        self.phys_world.update(dt)

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.mouse_pin.relocate(Vec(x, y))
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.G:
            self.force_gc = not self.force_gc
        else:
            super().on_key_press(symbol, modifiers)

    def on_draw(self):
        self.clear()
        self.phys_world.draw()
        print(pyglet.clock.get_fps(), end="      \r")

        if self.force_gc:
            gc.collect()


if __name__ == '__main__':
    window = Window(resizable=True, vsync=True, width=1000, height=1000)
    pyglet.app.run()
