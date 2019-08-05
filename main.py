#!./venv/bin/python3

import time
import math
import gc

import pyglet
from pyglet.window import key

from base import *
from phys import *
from collision import *


class DrawableWorld(PhysWorld):
    def draw(self):
        # Draw springs.
        for s in self._springs:
            if s.slack:
                colour = (0, 0, 255)
            else:
                colour = (0, 255, 0)

            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2f', tuple(s.get_end1_join_pos() + s.end1.pos)
                      + tuple(s.get_end2_join_pos() + s.end2.pos)
                ),
                ('c3B', colour * 2)
            )

        # Test for collision between the objects (yes => turn red).
        polygons = tuple(map(lambda o: Rect(x=o.pos.x,
                                      y=o.pos.y,
                                      w=200 * min(o.mass, 1),
                                      h=400 * min(o.mass, 1),
                                      angle=o.ang,
                                      colour=(200, 255, 255)
                                      ).get_poly(),
                       self._objects))

        def callback(o1, o2, axis=None):
            print(axis)
            #input()
            o1.colour = (255, 0, 0)
            o2.colour = (255, 0, 0)
            
            for v in o1.vertices:
                v -= axis / 1#00_000
        collide_all(polygons, callback=callback)

        # Draw polygons.
        for verts, colour in polygons:
            n_verts = len(verts)
            pyglet.graphics.draw(
                    n_verts,
                    pyglet.gl.GL_POLYGON,
                    ('v2f', tuple(flatten(verts))),
                    ('c3B', colour * n_verts)
                    )


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse = (0, 0)
        self.rect = Rect(x=250, y=250, w=100, h=200)
        self.force_gc = False
        self.time = 0

        #self.p = PhysObj(pos=Vec(x=500, y=450), mass=0.5, ang=0,
        #                   moi=0.5 * (100**2 + 200**2) / 12)
        #point2 = PhysObj(pos=Vec(x=300, y=300), mass=0.1, ang=0,
        #                   moi=0.1 * (100**2 + 200**2) / 12)

        #self.pin = Pin(pos=Vec(450, 400))
        #self.mouse_pin = Pin(pos=Vec(450, 400))

        #self.s = Spring(stiffness=0.99, end1=self.mouse_pin, end2=self.p,
        #                slack_length=100, end2_join_pos=Vec(50, 100))

        #spring1 = Spring(stiffness=0.75, end1=self.p, end2=point2,
        #                 end1_join_pos=Vec(-50, -100))
        #spring2 = Spring(stiffness=0.45, end1=point2, end2=self.pin,
        #                 end1_join_pos=Vec(-10, 20))

        #self.phys_world = DrawableWorld()
        #self.phys_world.gravity.y = -9.81
        #self.phys_world.add_obj(self.p, point2)
        #self.phys_world.add_spring(self.s, spring1, spring2)

        self.phys_world = DrawableWorld()
        self.phys_world.gravity.y = -9.81
        self.phys_world.add_obj(Pin(pos=Vec(x=450, y=400)),
                                PhysObj(pos=Vec(450, 900), mass=0.5, ang=0,
                                        moi=1000))

        pyglet.clock.schedule_interval(self.periodic_update, 1/120)
        #pyglet.clock.schedule(self.periodic_update)

    def periodic_update(self, dt):
        self.time += 1/120#dt

        #self.mouse_pin.relocate(Vec(x=500 + 250*math.cos(self.time),
        #                            y=750 - 250*math.sin(self.time)))

        self.phys_world.update(dt)
        #print(self.phys_world._objects[0].pos)

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
        #print(pyglet.clock.get_fps(), end="      \r")

        if self.force_gc:
            gc.collect()


if __name__ == '__main__':
    window = Window(resizable=True, vsync=True, width=1000, height=1000)
    pyglet.app.run()
