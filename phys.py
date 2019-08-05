"""Classes and functions for emulating 2D physics"""

from base import *


__all__ = ['PhysWorld',
           'PhysObj', 'Projectile', 'Pin',
           'Spring']


class PhysObj:
    """A basic physics object."""
    def __init__(self, pos, mass, ang, moi):
        self.pos = pos
        self.mass = mass
        self.vel = Vec(x=0, y=0)
        self.acc = Vec(x=0, y=0)
        self.new_acc = Vec()

        # There is only one axis for roataion in 2D - the Z-axis.
        self.ang = ang
        self.ang_vel = 0
        self.ang_acc = 0
        self.new_ang_acc = 0
        self.moi = moi  # Moment of intertia


class PhysWorld:
    """A world to hold and simulate interaction of `PhysObj`s."""
    def __init__(self):
        self._objects = []
        self._springs = []
        self.gravity = Vec(0, 0)

    def add_obj(self, *objs):
        for obj in objs:
            if not isinstance(obj, PhysObj):
                raise TypeError(f"{obj} is not a PhysObj")

            self._objects.append(obj)

    def add_spring(self, *springs):
        for spring in springs:
            if not isinstance(spring, Spring):
                raise TypeError(f"{spring} is not a Spring")

            self._springs.append(spring)

    def update(self, dt):
        self.dampen(dt)
        self.update_spring(dt)
        self.update_turn(dt)
        self.update_move(dt)

    def dampen(self, dt):
        for obj in self._objects:
            obj.vel -= obj.vel * 0.1 * dt
            obj.ang_vel -= obj.ang_vel * 0.1 * dt

    def update_spring(self, dt):
        # Calculate spring forces and apply them.
        for spring in self._springs:
            # Compute force.
            length = spring.end2.pos + spring.get_end2_join_pos() \
                     - spring.end1.pos - spring.get_end1_join_pos()

            # Skip this string if it's sack.
            abs_length = abs(length)
            if abs_length < spring.slack_length:
                spring.slack = True
                continue
            else:
                spring.slack = False

            extention = length * (abs_length - spring.slack_length) \
                        / abs_length
            force = extention * spring.stiffness

            spring.end1.new_acc += force / spring.end1.mass
            spring.end2.new_acc -= force / spring.end2.mass

            # Compute torque for end1.
            torque1 = spring.get_end1_join_pos().cross(force) 
            spring.end1.new_ang_acc += torque1 / spring.end1.moi

            # .. for end2.
            torque2 = spring.get_end2_join_pos().cross(force)
            spring.end2.new_ang_acc -= torque2 / spring.end2.moi

    def update_move(self, dt):
        for obj in self._objects:
            # Apply gravity.
            obj.new_acc += self.gravity

            # Calculate new position using Velocty Verlet.
            obj.vel += (obj.acc + obj.new_acc) * dt / 2
            obj.acc = obj.new_acc
            obj.pos += obj.vel*dt + obj.new_acc*dt*dt/2
            obj.new_acc = Vec(0, 0)

    def update_turn(self, dt):
        for obj in self._objects:
            # Calculate new oreintation using Velocity Verlet.
            obj.ang_vel += (obj.ang_acc + obj.new_ang_acc) * dt / 2
            obj.ang_acc = obj.new_ang_acc
            obj.ang += obj.ang_vel*dt + obj.new_ang_acc*dt*dt/2
            obj.new_ang_acc = 0

    def get_state(self):
        """Get the positions and velocities of al objects in self."""
        return "".join(flatten(
                        ("obj p=", str(obj.pos), " v=", str(obj.vel), "\n")
                        for obj in self._objects))


class Projectile(PhysObj):
    """A PhysObj that has no rotation or width."""
    def __init__(self, pos, mass):
        super().__init__(pos, mass, ang=0, moi=float('inf'))


class Pin(Projectile):
    """A fixed point in space.
    
    IMPORTANT NOTE:
     In order to move the pin, its `relocate` method must be used.
     This is as the `Pin` ignores messages to move itself that seem to
     come form a `PhysWorld` (ie that are sent using `Pin.pos = ...`).
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
        pos = self.PinnedVec(x=pos.x, y=pos.y)
        super().__init__(pos=pos, mass=float('inf'))
        self.relocate(pos)

    def relocate(self, value):
        self._pos = self.PinnedVec(x=value.x, y=value.y)


class Spring:
    """A spring connecting two `PhysObj`s.

    stiffness - the spring constant.
    end1 - an object attached to one end.
    end2 - an object attached to the other end.
    slack_length - the distance between end1 and end2 before the string
        exherts any force (default=0).
    end1_join_pos - the displacement from the centre of end1's object
         of that end of the spring (default=no displacement).
    end2_join_pos - the displacement from the centre of end2's object
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
