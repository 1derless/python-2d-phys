#!./venv/bin/python3

import time
import math
import gc

import pyglet
from pyglet.window import key

from base import *
from phys import *
from collision import *
from colliding_world import *


class Entity(PhysObj, Collider):
    def __init__(self, pos, mass, ang, moi, vertices, colour=(255, 255, 255)):
        super().__init__(pos, mass, ang, moi)

        self.vertices = vertices
        self.colour = colour

    def get_vertices(self):
        return [vertex.rotate(self.ang) + self.pos for vertex in self.vertices]


class FrozenEntity(Pin, Collider):
    def __init__(self, pos, vertices, colour=(255, 255, 255)):
        super().__init__(pos)

        self.vertices = vertices
        self.colour = colour

    def get_vertices(self):
        return [vertex + self.pos for vertex in self.vertices]


class DrawableWorld(CollidingWorld):
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

        # Draw polygons.
        for obj in self._objects:
            verts = obj.get_vertices()
            n_verts = len(verts)
            pyglet.graphics.draw(n_verts, pyglet.gl.GL_POLYGON,
                    ('v2f', tuple(flatten(verts))),
                    ('c3B', obj.colour * n_verts)
            )


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse = (0, 0)
        self.rect = Rect(x=250, y=250, w=100, h=200)
        self.force_gc = False
        self.time = 0

        self.obj1 = Entity(
           pos=Vec(450, 250),
           mass=0.5,
           ang=3.141593 / 4,
           moi=1000,
           colour=(0, 0, 255),
           vertices=[
               Vec(x=-50., y=-50.),
               Vec(x= 50., y=-50.),
               Vec(x= 50., y= 50.),
               Vec(x=-50., y= 50.),
             ]
            )

        self.phys_world = DrawableWorld()
        self.phys_world.gravity.y = -9.81
        self.phys_world.add_obj(
            self.obj1,
            Entity(pos=Vec(250, 200), mass=0.5, ang=0, moi=1000,
                   colour=(0, 255, 0),
                   vertices=[Vec(x=-50., y=-50.),
                             Vec(x= 50., y=-50.),
                             Vec(x= 50., y= 50.),
                             Vec(x=-50., y= 50.),
                             ]),
            FrozenEntity(pos=Vec(450, 50),
                   vertices=[Vec(x=-100., y=-25.),
                             Vec(x= 100., y=-25.),
                             Vec(x= 100., y= 25.),
                             Vec(x=-100., y= 25.),
                             ]),
        )
        self.phys_world._objects[0].vel = Vec(x=-100, y=0)
        self.phys_world._objects[1].vel = Vec(x= 100, y=0)


        import random
        for _ in range(4):
            self.phys_world.add_obj(
                Entity(
                   pos=Vec(random.randint(0, 600), random.randint(450, 650)),
                   mass=0.5,
                   ang=3.141593 / 4,
                   moi=1000,
                   colour=(random.randint(63, 255),) * 3,
                   vertices=[
                       Vec(x=-50., y=-50.),
                       Vec(x= 50., y=-50.),
                       Vec(x= 50., y= 50.),
                       Vec(x=-50., y= 50.),
                       ]
                    )
                )
            


        #pyglet.clock.schedule_interval(self.periodic_update, 1/120)
        pyglet.clock.schedule(self.periodic_update)

    def periodic_update(self, dt):
        self.time += dt

        self.phys_world.update(dt)
        for obj in self.phys_world._objects:
            obj.pos.x %= self.width
            obj.pos.y %= self.height

    def on_mouse_motion(self, x, y, _dx, _dy):
        #self.mouse_pin.relocate(Vec(x, y))
        self.obj1.pos = Vec(x, y)
        self.obj1.vel = Vec(0, 0)
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == key.G:
            self.force_gc = not self.force_gc
        elif symbol == key.SPACE:
            for obj in self.phys_world._objects:
                obj.vel = Vec(0, 0)
        else:
            super().on_key_press(symbol, modifiers)

    def on_draw(self):
        try:
            self.on_draw_()
        except Exception as e:
            raise e

    def on_draw_(self):
        self.clear()
        self.phys_world.draw()
        #print(pyglet.clock.get_fps(), end="      \r")

        if self.force_gc:
            gc.collect()


if __name__ == '__main__':
    window = Window(resizable=True, vsync=True, width=1000, height=1000)
    pyglet.app.run()
