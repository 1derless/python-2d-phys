#!./venv/bin/python3

import time
import math
import sys
import gc

import pyglet
from pyglet.window import key, mouse
import easygui

from base import *
from phys import *
from collision import *
from colliding_world import *
import gui
import load_system

test_material = Material(
    static_friction=0.4,
    dynamic_friction=0.2,
    restitution=0.2,
    density=0.00005,  # todo: adjust when density is implemented
)


class DrawCollider(Collider):
    def __init__(self, pos, mass, ang, moi, vertices, colour=(255, 255, 255)):
        centre = sum(vertices, Vec(0, 0)) / len(vertices)
        vertices = [v - centre for v in vertices]

        super().__init__(vertices, test_material, pos, ang, mass, moi)

        self.colour = colour

    def get_vertices(self):
        return [vertex.rotate(self.ang) + self.pos for vertex in self.vertices]


class Hexagon(DrawCollider):
    vertices = [
        Vec(100, 0),
        Vec(50, 87),
        Vec(-50, 87),
        Vec(-100, 0),
        Vec(-50, -87),
        Vec(50, -87),
    ]

    def __init__(self, scale, pos, ang, material, colour=(255, 255, 255)):
        # mass = area * density
        length = scale * 100
        mass = 3 / 2 * 3**0.5 * length**2 * material.density
        moi = 5 / 16 * 3**0.5 * length**4 * material.density

        vertices = [v * scale for v in Hexagon.vertices]

        super().__init__(pos, mass, ang, moi, vertices, colour)


class FrozenEntity(DrawCollider):
    def __init__(self, pos, vertices, colour=(255, 255, 255)):
        super().__init__(pos, mass=float('inf'), moi=float('inf'), vertices=vertices, ang=0)

        self.vertices = vertices
        self.colour = colour

    def get_vertices(self):
        return [vertex + self.pos for vertex in self.vertices]


class DrawableWorld(CollidingWorld):
    def __init__(self):
        super().__init__()

        self.draw_impulses = True

    def draw(self):
        # Draw springs.
        for s in self.springs:
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
        for obj in self.entities:
            verts = obj.get_vertices()
            n_verts = len(verts)
            pyglet.graphics.draw(n_verts, pyglet.gl.GL_LINE_LOOP,
            #pyglet.graphics.draw(n_verts, pyglet.gl.GL_POLYGON,
                    ('v2f', tuple(flatten(verts))),
                    ('c3B', obj.colour * n_verts)
            )

        # Draw impulses.
        batch = pyglet.graphics.Batch()  # Batch draw calls to improve performance.
        if self.draw_impulses:
            for imp in self.imps:
                # if abs(imp[1]) < 1:
                #     continue

                batch.add(2, pyglet.gl.GL_LINES, None,
                    ('v2f', (imp[0].x + imp[2].x,
                             imp[0].y + imp[2].y,
                             imp[0].x + imp[2].x + imp[1].x,
                             imp[0].y + imp[2].y + imp[1].y)
                    ),
                    ('c3B', (255, 0, 0) * 2)
                )

            batch.draw()


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.force_gc = False
        self.time = 0

        self.phys_world = DrawableWorld()
        self.phys_world.gravity.y = -100
        self.phys_world.add_ent(
            Hexagon(
                scale=0.75,
                pos=Vec(500, 500),
                ang=-1,
                material=test_material,
            ),
            FrozenEntity(pos=Vec(450, 50),
                   vertices=[Vec(x=-9000., y=-75.),
                             Vec(x= 9000., y=-75.),
                             Vec(x= 9000., y= 25.),
                             Vec(x=-9000., y= 25.),
                             ]),
            FrozenEntity(pos=Vec(0, 0),
                   vertices=[Vec(x=-10., y=0.),
                             Vec(x= 10., y=0.),
                             Vec(x= 10., y=1000.),
                             Vec(x=-10., y=1000.),
                             ]),
            FrozenEntity(pos=Vec(0, 0),
                   vertices=[Vec(x=840., y=0.),
                             Vec(x=860., y=0.),
                             Vec(x=860., y=1000.),
                             Vec(x=840., y=1000.),
                             ]),
        )

        pyglet.clock.schedule_interval(self.periodic_update, 1/120)
        #pyglet.clock.schedule(self.periodic_update)

    def periodic_update(self, dt):
        dt = 1 / 120
        self.time += dt

        steps = 1
        for _ in range(steps):
            self.phys_world.update(dt / steps)

        print(f'{1/dt} fps' if dt > 0 else '', end='\r')

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.phys_world.add_ent(
                Hexagon(
                    scale=1,
                    pos=Vec(x, y),
                    ang=0,
                    material=test_material,
                )
            )
        elif button == mouse.RIGHT:
            for ent in self.phys_world.entities:
                if 0 > collide_point(Vec(x, y), ent.get_vertices()):
                    print('Removed', ent)
                    self.phys_world.remove_ent(ent)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.G:
            self.force_gc = not self.force_gc

        elif symbol == key.SPACE:
            for obj in self.phys_world.entities:
                obj.vel = Vec(0, 0)
                obj.new_vel = Vec(0, 0)
                obj.ang_vel = 0
                obj.new_ang_vel = 0

        elif symbol == key.M:
            global test_material

            test_material = gui.get_material() or test_material

        elif symbol == key.D:
            self.phys_world.draw_impulses = not self.phys_world.draw_impulses

        else:
            super().on_key_press(symbol, modifiers)

    def on_draw(self):
        try:
            self.on_draw_()
        except Exception as e:
            raise e

    def on_draw_(self):
        self.clear()
        #pyglet.graphics.draw(5, pyglet.gl.GL_POLYGON,
        #    ('v2f', [0.0, 0.0,  self.width, 0.0,  self.width, self.height,  0.0, self.height,  0.0, 0.0]),
        #    ('c4B', [0, 0, 0, 255] * 5)
        #)
        DrawableWorld.draw(self.phys_world)
        #print(pyglet.clock.get_fps(), end="      \r")

        if self.force_gc:
            gc.collect()


if __name__ == '__main__':
    window = Window(resizable=True, vsync=False, width=1000, height=1000)
    pyglet.app.run()
