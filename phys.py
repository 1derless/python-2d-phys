"""Classes and functions for emulating 2D physics"""

from base import *


__all__ = ['System',
           'Entity', 'Projectile', 'Pin',
           'Spring']


class Entity:
    """A basic physics object."""
    def __init__(self, pos, mass, ang, moi):
        self.pos = pos
        self.mass = mass
        self.vel = Vec(x=0, y=0)
        self.acc = Vec(x=0, y=0)
        self.new_pos = self.pos
        self.new_vel = self.vel
        self.new_acc = self.acc

        # There is only one axis for rotation in 2D - the Z-axis.
        self.ang = ang
        self.ang_vel = 0
        self.ang_acc = 0
        self.new_ang = ang
        self.new_ang_vel = 0
        self.new_ang_acc = 0
        self.moi = moi  # Moment of inertia


class System:
    """A world to hold and simulate interaction of `Entity`s."""
    def __init__(self, gravity=Vec(0, 0)):
        self.entities = []
        self.springs = []
        self.gravity = gravity

    def add_ent(self, *entities):
        for ent in entities:
            if not isinstance(ent, Entity):
                raise TypeError(f"{ent} is not an Entity")

            self.entities.append(ent)

    def remove_ent(self, *entities):
        for ent in entities:
            self.entities.remove(ent)

    def add_spring(self, *springs):
        for spring in springs:
            if not isinstance(spring, Spring):
                raise TypeError(f"{spring} is not a Spring")

            self.springs.append(spring)

    def remove_spring(self, *springs):
        for spring in springs:
            self.springs.remove(spring)

    def update(self, dt):
        self.damp(dt)
        self.update_spring(dt)
        self.update_turn(dt)
        self.update_move(dt)

    def damp(self, dt):
        for ent in self.entities:
            ent.new_vel -= ent.vel * 0.1 * dt
            ent.ang_vel -= ent.ang_vel * 0.1 * dt

    def update_spring(self, dt):
        # Calculate spring forces and apply them.
        for spring in self.springs:
            length = spring.end2.pos + spring.get_end2_join_pos() \
                     - spring.end1.pos - spring.get_end1_join_pos()

            # Skip this string if it's sack.
            abs_length = abs(length)
            if abs_length < spring.slack_length:
                spring.slack = True
                continue
            else:
                spring.slack = False

            # Compute force using Hooke's law.
            extension = length * (abs_length - spring.slack_length) \
                        / abs_length
            force = extension * spring.stiffness

            spring.end1.new_acc += force / spring.end1.mass
            spring.end2.new_acc -= force / spring.end2.mass

            # Compute torque for end1.
            torque1 = spring.get_end1_join_pos().cross(force) 
            spring.end1.new_ang_acc += torque1 / spring.end1.moi

            # .. for end2.
            torque2 = spring.get_end2_join_pos().cross(force)
            spring.end2.new_ang_acc -= torque2 / spring.end2.moi

    def update_move(self, dt):
        for ent in self.entities:
            if ent.mass == float('inf'):
                continue

            # Apply gravity.
            ent.new_acc += self.gravity

            # Calculate new position using Velocity Verlet.
            ent.vel = ent.new_vel + (ent.acc + ent.new_acc) * dt / 2
            ent.pos = ent.new_pos + ent.vel*dt + ent.new_acc*dt*dt/2
            ent.acc = ent.new_acc

            ent.new_pos = ent.pos
            ent.new_vel = ent.vel
            ent.new_acc = Vec(0, 0)

    def update_turn(self, dt):
        for ent in self.entities:
            # Calculate new orientation using Velocity Verlet.
            ent.ang_vel = 1 * ent.new_ang_vel + \
                          (ent.ang_acc + ent.new_ang_acc) * dt / 2
            ent.ang = ent.new_ang + ent.ang_vel*dt + ent.new_ang_acc*dt*dt/2
            ent.ang_acc = ent.new_ang_acc

            ent.new_ang = ent.ang
            ent.new_ang_vel = ent.ang_vel
            ent.new_ang_acc = 0

    def get_state(self):
        """Get the positions and velocities of all entities in self."""
        return "".join(flatten(
                        ("ent p=", str(ent.pos), " v=", str(ent.vel), "\n")
                        for ent in self.entities))


class Projectile(Entity):
    """A Entity that has no rotation or width."""
    def __init__(self, pos, mass):
        super().__init__(pos, mass, ang=0, moi=float('inf'))


class Pin(Projectile):
    """A fixed point in space.
    
    IMPORTANT NOTE:
     In order to move the pin, its `relocate` method must be used.
     This is as the `Pin` ignores messages to move itself that seem to
     come form a `System` (ie that are sent using `Pin.pos = ...`).
    """

    class PinnedVec(Vec):
        def __iadd__(self, other):
            return self

        def __isub__(self, other):
            return self

        def __imul__(self, other: float):
            return self

        def __itruediv__(self, other: float):
            return self

        def rotate_inplace(self, other):
            pass

    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        pass

    def __init__(self, pos):
        self.relocate(pos)
        pos = self.PinnedVec(x=pos.x, y=pos.y)
        super().__init__(pos=pos, mass=float('inf'))

    def relocate(self, value):
        self._pos = self.PinnedVec(x=value.x, y=value.y)


class Spring:
    """A spring connecting two `Entity`s.

    stiffness - the spring constant.
    end1 - an entity attached to one end.
    end2 - an entity attached to the other end.
    slack_length - the distance between end1 and end2 before the string
        exerts any force (default=0).
    end1_join_pos - the displacement from the centre of end1's entity
         of that end of the spring (default=no displacement).
    end2_join_pos - the displacement from the centre of end2's entity
         of that end of the spring(default=no displacement).
    """
    def __init__(self, stiffness, end1, end2, slack_length=0,
                 end1_join_pos=None, end2_join_pos=None):
        self.stiffness = stiffness
        self.slack_length = slack_length
        self.slack = False
        self.end1 = end1
        self.end2 = end2

        if end1_join_pos is None:
            self.end1_join_pos = Vec(0, 0)
        else:
            self.end1_join_pos = end1_join_pos

        if end2_join_pos is None:
            self.end2_join_pos = Vec(0, 0)
        else:
            self.end2_join_pos = end2_join_pos

    def get_end1_join_pos(self):
        """Calculates the rotation-aware join pos of end1."""
        return self.end1_join_pos.rotate(self.end1.ang)

    def get_end2_join_pos(self):
        """Calculates the rotation-aware join pos of end2."""
        return self.end2_join_pos.rotate(self.end2.ang)
