#!./venv/bin/python3

import time
import math
import sys
import gc
import enum
import json

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
    density=1,  # todo: adjust when density is implemented
)


class DrawCollider(Collider):
    def __init__(self, pos, mass, ang, moi, vertices, colour=(255, 255, 255)):
        centre = sum(vertices, Vec(0, 0)) / len(vertices)
        vertices = [v - centre for v in vertices]

        super().__init__(vertices, test_material, pos, ang, mass, moi)

        self.colour = colour

    def get_vertices(self):
        return [vertex.rotate(self.ang) + self.pos for vertex in self.vertices]


class Triangle(DrawCollider):
    vertices = [
        Vec(-1, 0),
        Vec(1, 0),
        Vec(0, 3**.5),
    ]

    def __init__(self, scale, pos, ang, material, colour=(255, 255, 255)):
        scale = 100
        length = scale * 2
        # mass = 3 / 2 * 3**0.5 * length**2 * material.density
        # moi = 5 / 16 * 3**0.5 * length**4 * material.density

        mass = 3**0.5 / 4 * length**2 * material.density
        moi = length**2 * material.density

        # print(moi, mass)
        mass = 17320.508075689 * material.density
        moi = 3608440_00 * material.density

        vertices = [v * scale for v in Triangle.vertices]

        super().__init__(pos, mass, ang, moi, vertices, colour)


class Hexagon(DrawCollider):
    vertices = [
        Vec(100, 0),
        Vec(50, 87),
        Vec(-50, 87),
        Vec(-100, 0),
        Vec(-50, -87),
        Vec(50, -87),
    ]
    vertices = list(map(lambda v: v + Vec(100, 100), vertices))

    def __init__(self, scale, pos, ang, material, colour=(255, 255, 255)):
        # mass = area * density
        length = scale * 100
        # mass = 3 / 2 * 3**0.5 * length**2 * material.density
        # moi = 5 / 16 * 3**0.5 * length**4 * material.density

        mass = 3**0.5 / 2 * length**2 * material.density
        moi = 5 / 16 * 3**0.5 * length**4 * material.density

        # print(moi, mass)

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
    def __init__(self, gravity=Vec(0.0, 0.0)):
        super().__init__()

        self.draw_impulses = True

    def draw(self):
        try:
            self.draw_()
        except Exception as e:
            print(e)
            assert False
            input()

    def draw_(self):
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

            if hasattr(obj, 'colour'):
                colour = obj.colour
            else:
                colour = (255, 255, 255)

            pyglet.graphics.draw(n_verts, pyglet.gl.GL_POLYGON,
                    ('v2f', tuple(flatten(verts))),
                    ('c3B', colour[:3] * n_verts)
            )


            if False:
                aabb = make_aabb(verts)
                vl = pyglet.graphics.vertex_list(4, ('v2f', (aabb[0], aabb[1],
                                                             aabb[2], aabb[1],
                                                             aabb[2], aabb[3],
                                                             aabb[0], aabb[3],
                                                             )),
                                                 ('c3B', (127, 255, 255) * 4)
                                                 )
                vl.draw(pyglet.gl.GL_LINE_LOOP)

        # Draw impulses.
        imp_verts = []
        if self.draw_impulses:
            for imp in self.imps:
                if abs(imp[1]) < 10:
                    imp[-1] -= 4
                    continue

                imp_verts.extend(
                    (imp[0].x + imp[2].x,
                     imp[0].y + imp[2].y,
                     imp[0].x + imp[2].x + imp[1].x / 500,
                     imp[0].y + imp[2].y + imp[1].y / 500)
                    ),

            # Draw all impulses in one go.
            if imp_verts:
                no_verts = len(imp_verts) // 2
                pyglet.graphics.draw(
                    no_verts,
                    pyglet.gl.GL_LINES,
                    ('v2f', imp_verts),
                    ('c4B', (255, 0, 0, 255) * no_verts),
                )


class EditorState(enum.Enum):
    EDIT = enum.auto()
    PLAY = enum.auto()


class LabeledButton:
    def __init__(self, text, x, y, font_size, colour=(255, 255, 255, 255), bg_colour=(0, 0, 0, 255)):
        self.label = pyglet.text.Label(
            text=text,
            x=x,
            y=y,
            font_size=font_size,
            anchor_x='left',
            anchor_y='bottom',
            color=colour
        )
        self.bg_colour = bg_colour

    def check_click(self, x, y):
        return (self.label.x <= x <= self.label.x + self.label.content_width
            and self.label.y <= y <= self.label.y + self.label.content_height)

    def draw(self):
        vertices = (self.label.x,                            self.label.y,
                    self.label.x + self.label.content_width, self.label.y,
                    self.label.x + self.label.content_width, self.label.y + self.label.content_height,
                    self.label.x,                            self.label.y + self.label.content_height)
        pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON, ('v2f', vertices), ('c4B', self.bg_colour * 4))

        self.label.draw()


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = 0

        self.colour = (255, 255, 255, 255)
        self.state = EditorState.EDIT

        self.selection_for_spring = None
        self.attributes_for_spring = (10000, 0)

        self.label_play = LabeledButton(
                text='Play',
                x=0,
                y=0,
                font_size=50,
            )

        self.label_pause = LabeledButton(
            text='Pause',
            x=0,
            y=0,
            font_size=50,
        )

        self.phys_world = DrawableWorld()
        self.phys_world.gravity.y = -100
        self.phys_world.add_ent(
            Hexagon(
                scale=1,
                pos=Vec(500, 500),
                ang=-1,
                material=test_material,
            ),
            Hexagon(
                scale=1,
                pos=Vec(250, 250),
                ang=-1,
                material=test_material,
                colour=(255, 127, 127),
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

        for i in range(100):
            self.phys_world.add_ent(
                Hexagon(
                    scale=1,
                    pos=Vec(250, 250),
                    ang=-1,
                    material=test_material,
                    colour=(255, 127, 127),
                ),
            )

        self.phys_world.add_spring(
            Spring(stiffness=10000,
                   end1=self.phys_world.entities[0],
                   end2=self.phys_world.entities[1],
                   end1_join_pos=Vec(100, 0),
                   end2_join_pos=Vec(50, 87))
        )

        pyglet.clock.schedule_interval(self.periodic_update, 1/30)
        #pyglet.clock.schedule(self.periodic_update)

        print(self.phys_world.serialise())
        #x = input()
        d = json.loads('''
{"springs": [{"stiffness": 10000, "slack_length": 0, "end1": "93982084042720", "end2": "93982084042776"}], "entities": {"93982084042720": {"mass": 8660.254037844386, "moi": 54126587.73652741, "pos": {"x": 500, "y": 500}, "vel": {"x": 0.0, "y": 0.0}, "acc": {"x": 0.0, "y": 0.0}, "ang": -1, "ang_vel": 0, "ang_acc": 0, "material": "93982085918632", "shape": "93982077865112"}, "93982084042776": {"mass": 8660.254037844386, "moi": 54126587.73652741, "pos": {"x": 250, "y": 250}, "vel": {"x": 0.0, "y": 0.0}, "acc": {"x": 0.0, "y": 0.0}, "ang": -1, "ang_vel": 0, "ang_acc": 0, "material": "93982085918632", "shape": "93982077865136"}, "93982084042832": {"mass": Infinity, "moi": Infinity, "pos": {"x": 450, "y": 50}, "vel": {"x": 0.0, "y": 0.0}, "acc": {"x": 0.0, "y": 0.0}, "ang": 0, "ang_vel": 0, "ang_acc": 0, "material": "93982085918632", "shape": "93982077865160"}, "93982084042888": {"mass": Infinity, "moi": Infinity, "pos": {"x": 0, "y": 0}, "vel": {"x": 0.0, "y": 0.0}, "acc": {"x": 0.0, "y": 0.0}, "ang": 0, "ang_vel": 0, "ang_acc": 0, "material": "93982085918632", "shape": "93982077865184"}, "93982084042944": {"mass": Infinity, "moi": Infinity, "pos": {"x": 0, "y": 0}, "vel": {"x": 0.0, "y": 0.0}, "acc": {"x": 0.0, "y": 0.0}, "ang": 0, "ang_vel": 0, "ang_acc": 0, "material": "93982085918632", "shape": "93982077865208"}}, "gravity": {"x": 0, "y": -100}, "shapes": {"93982077865112": [{"x": 100.0, "y": 0.0}, {"x": 50.0, "y": 87.0}, {"x": -50.0, "y": 87.0}, {"x": -100.0, "y": 0.0}, {"x": -50.0, "y": -87.0}, {"x": 50.0, "y": -87.0}], "93982077865136": [{"x": 100.0, "y": 0.0}, {"x": 50.0, "y": 87.0}, {"x": -50.0, "y": 87.0}, {"x": -100.0, "y": 0.0}, {"x": -50.0, "y": -87.0}, {"x": 50.0, "y": -87.0}], "93982077865160": [{"x": -9000.0, "y": -75.0}, {"x": 9000.0, "y": -75.0}, {"x": 9000.0, "y": 25.0}, {"x": -9000.0, "y": 25.0}], "93982077865184": [{"x": -10.0, "y": 0.0}, {"x": 10.0, "y": 0.0}, {"x": 10.0, "y": 1000.0}, {"x": -10.0, "y": 1000.0}], "93982077865208": [{"x": 840.0, "y": 0.0}, {"x": 860.0, "y": 0.0}, {"x": 860.0, "y": 1000.0}, {"x": 840.0, "y": 1000.0}]}, "materials": {"93982085918632": {"static_friction": 0.4, "dynamic_friction": 0.2, "restitution": 0.2, "density": 1}}}
''')
        print(d['shapes'])
        self.phys_world = DrawableWorld.from_dict(d)
        print(self.phys_world.entities[0].pos)

    def periodic_update(self, dt):
        print(f'{1/dt} fps' if dt > 0 else '', end='\n')

        if self.state == EditorState.PLAY:
            dt = 1 / 30
            self.time += dt

            steps = 1
            for _ in range(steps):
                self.phys_world.update(dt / steps)

        elif self.state == EditorState.EDIT:
            pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            # If clicked on play button:
            if self.label_play.check_click(x, y) and self.state == EditorState.EDIT:
                self.state = EditorState.PLAY
            elif self.label_pause.check_click(x, y) and self.state == EditorState.PLAY:
                self.state = EditorState.EDIT

            # If clicked on no button, add shape:
            else:
                self.phys_world.add_ent(
                    Triangle(
                        scale=75,
                        pos=Vec(x, y),
                        ang=0,
                        material=test_material,
                        colour=self.colour,
                    )
                )

        elif button == mouse.RIGHT:
            for ent in self.phys_world.entities:
                if 0 > collide_point(Vec(x, y), ent.get_vertices()):
                    end2_join_pos = (Vec(x, y) - ent.pos).rotate(-ent.ang)

                    if self.selection_for_spring is None:
                        self.selection_for_spring = (ent, end2_join_pos)

                    elif self.selection_for_spring[0] is not ent:
                        self.phys_world.add_spring(
                            Spring(stiffness=self.attributes_for_spring[0],
                                   slack_length=self.attributes_for_spring[1],
                                   end1=self.selection_for_spring[0],
                                   end2=ent,
                                   end1_join_pos=self.selection_for_spring[1],
                                   end2_join_pos=end2_join_pos,
                                   )
                        )

                        self.selection_for_spring = None

        elif button == mouse.MIDDLE:
            for ent in self.phys_world.entities:
                if 0 > collide_point(Vec(x, y), ent.get_vertices()):
                    # print('Removed', ent)
                    self.phys_world.remove_ent(ent)

                    if self.selection_for_spring is not None and self.selection_for_spring[0] is ent:
                        self.selection_for_spring = None

                    self.phys_world.springs = [s for s in self.phys_world.springs
                                               if s.end1 is not ent and s.end2 is not ent]

    def on_key_press(self, symbol, modifiers):
        if symbol == key.G:
            self.attributes_for_spring = gui.get_spring() or self.attributes_for_spring

        elif symbol == key.H:
            for spring in self.phys_world.springs:
                print(spring.end1, spring.end2)

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

        elif symbol == key.C:
            self.colour = gui.get_colour() or self.colour

        else:
            super().on_key_press(symbol, modifiers)

    def on_draw(self):
        try:
            self.on_draw_()
        except Exception as e:
            raise e

    def on_draw_(self):
        self.clear()
        DrawableWorld.draw(self.phys_world)

        if self.state == EditorState.EDIT:
            self.label_play.draw()

        elif self.state == EditorState.PLAY:
            self.label_pause.draw()


if __name__ == '__main__':
    window = Window(resizable=True, vsync=False, width=1000, height=1000)

    import cProfile
    cProfile.run('[window.phys_world.update(1/120) for _ in range(1000)]')
    # input()

    # cProfile.run('pyglet.app.run()')
    pyglet.app.run()
