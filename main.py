#!./venv/bin/python3

import time
import math
import gc

import pyglet
from pyglet.window import key
import easygui

from base import *
from phys import *
from collision import *
from colliding_world import *
import load_system


class Entity(Entity, Collider):
    def __init__(self, pos, mass, ang, moi, vertices, colour=(255, 255, 255)):
        super().__init__(pos, mass, ang, moi)
        centre = sum(vertices, Vec(0, 0)) / len(vertices)
        vertices = [v - centre for v in vertices]

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
        for obj in self._entities:
            verts = obj.get_vertices()
            n_verts = len(verts)
            pyglet.graphics.draw(n_verts, pyglet.gl.GL_LINE_LOOP,
            #pyglet.graphics.draw(n_verts, pyglet.gl.GL_POLYGON,
                    ('v2f', tuple(flatten(verts))),
                    ('c3B', obj.colour * n_verts)
            )

        # Draw impulses.
        for imp in self.imps:
            if abs(imp[1]) < 3:
                continue

            k = 1000
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2f', (imp[0].x + imp[2].x,
                         imp[0].y + imp[2].y,
                         imp[0].x + imp[2].x + imp[1].x,
                         imp[0].y + imp[2].y + imp[1].y)
                ),
                ('c3B', (255, 0, 0) * 2)
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
           ang=3.141593 / 3,
           moi=300,
           colour=(0, 0, 255),
           vertices=[
               Vec(x=-50., y=-25.),
               #Vec(x= 50., y=-50.),
               Vec(x= 50., y=-25.),
               Vec(x=  0., y= 25.),
             ]
            )
        self.obj2 = Entity(
           pos=Vec(450, 150),
           mass=0.5,
           ang=0.0,
           moi=400,
           colour=(255, 0, 255),
           vertices=[
               Vec(x=-50., y=-50.),
               #Vec(x= 50., y=-50.),
               Vec(x= 50., y=-50.),
               Vec(x=  0., y= 50.),
             ]
            )

        self.phys_world = DrawableWorld()
        self.phys_world.gravity.y = -100
        self.phys_world.add_ent(
            self.obj1,
        #    Entity(pos=Vec(250, 200), mass=0.5, ang=0, moi=1000,
        #           colour=(0, 255, 0),
        #           vertices=[Vec(x=-50., y=-50.),
        #                     Vec(x= 50., y=-50.),
        #                     Vec(x= 50., y= 50.),
        #                     Vec(x=-50., y= 50.),
        #                     ]),
        #    Entity(pos=Vec(150, 200), mass=0.25, ang=0, moi=1000,
        #           colour=(0, 255, 255),
        #           vertices=[Vec(x=-50., y=-50.),
        #                     #Vec(x= 50., y=-50.),
        #                     Vec(x= 50., y= 50.),
        #                     Vec(x=-50., y= 50.),
        #                     ]),
            self.obj2,
            FrozenEntity(pos=Vec(450, 50),
                   vertices=[Vec(x=-9000., y=-75.),
                             Vec(x= 9000., y=-75.),
                             Vec(x= 9000., y= 25.),
                             Vec(x=-9000., y= 25.),
                             ]),
            FrozenEntity(pos=Vec(0, 0),
                   vertices=[Vec(x= 500., y=-75.),
                             Vec(x= 550., y=-75.),
                             Vec(x=9050., y=1000.),
                             Vec(x=9000., y=1000.),
                             ]),
            FrozenEntity(pos=Vec(0, 0),
                   vertices=[Vec(x=-10., y=0.),
                             Vec(x= 10., y=0.),
                             Vec(x= 10., y=1000.),
                             Vec(x=-10., y=1000.),
                             ]),
            FrozenEntity(pos=Vec(0, 0),
                   vertices=[Vec(x=790., y=0.),
                             Vec(x=810., y=0.),
                             Vec(x=810., y=1000.),
                             Vec(x=790., y=1000.),
                             ]),
        #    self.obj2,
        )

        self.phys_world.add_spring(Spring(
            stiffness=0.5,
            end1=self.obj1,
            end1_join_pos=Vec(x=0., y=25.),
            end2=self.obj2,
            end2_join_pos=Vec(x=0., y=66.67),
            )
        )

        import random
        for i in range(10):
            self.phys_world.add_ent(
                Entity(
                   pos=Vec(random.randint(0, 600), 105 * i),
                   mass=0.5,
                   ang=3.141593 / 4,
                   moi=833,
                   colour=(random.randint(63, 255),) * 3,
                   vertices=[
                       Vec(x=-50., y=-50.),
                       Vec(x= 50., y=-50.),
                       Vec(x= 50., y= 50.),
                       Vec(x=-50., y= 50.),
                       ]
                    )
                )

        pyglet.clock.schedule_interval(self.periodic_update, 1/120)
        #pyglet.clock.schedule(self.periodic_update)

        ###############
        #load_system.save('test_v2.dat', self.phys_world)
        #self.phys_world = load_system.load(easygui.fileopenbox())
        #if version != 'version 1':
        #    raise TypeError('Wrong version file')
        ###############

    def periodic_update(self, dt):
        dt = 1 / 120
        self.time += dt

        steps = 1
        for _ in range(steps):
            self.phys_world.update(dt / steps)

        #for obj in self.phys_world._entities:
        #    obj.pos.x %= self.width
        #    obj.pos.y %= self.height

        print(1/dt if dt > 0 else "No time.", end='\r')

    def on_mouse_motion(self, x, y, _dx, _dy):
        #self.mouse_pin.relocate(Vec(x, y))
        self.obj1.new_pos = Vec(x, y)
        self.obj1.new_vel = Vec(0, 0)
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == key.G:
            self.force_gc = not self.force_gc
        elif symbol == key.SPACE:
            for obj in self.phys_world._entities:
                obj.vel = Vec(0, 0)
                obj.new_vel = Vec(0, 0)
                obj.ang_vel = 0
                obj.new_ang_vel = 0
        else:
            super().on_key_press(symbol, modifiers)

    def on_draw(self):
        try:
            self.on_draw_()
        except Exception as e:
            raise e

    def on_draw_(self):
        #self.clear()
        pyglet.graphics.draw(5, pyglet.gl.GL_POLYGON,
            ('v2f', [0.0, 0.0,  self.width, 0.0,  self.width, self.height,  0.0, self.height,  0.0, 0.0]),
            ('c4B', [0, 0, 0, 255] * 5)
        )
        DrawableWorld.draw(self.phys_world)
        print(pyglet.clock.get_fps(), end="      \r")

        if self.force_gc:
            gc.collect()


if __name__ == '__main__':
    window = Window(resizable=True, vsync=False, width=1000, height=1000)
    pyglet.app.run()
