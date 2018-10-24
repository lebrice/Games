import numpy as np
from typing import Tuple, List, NamedTuple
import arcade

from config import *
from utils import pairs
from collision_detection import circle_line_intersection


class Particle():
    next_particle_id = 0

    def __hash__(self):
        return hash(self.particle_id)

    def __eq__(self, other: object):
        if other.__class__ == self.__class__:
            return other.particle_id == self.particle_id
        return NotImplemented

    def __init__(self, position: Tuple[float, float], mass: float = 0):
        self.particle_id = Particle.next_particle_id
        Particle.next_particle_id += 1
        self.curr_pos = np.asarray(position, dtype=float)
        self.prev_pos = np.asarray(position, dtype=float)
        self.acceleration = np.zeros(2, float)
        self.attached_particles: Dict[Particle, float] = dict()
        self.inv_mass = 0 if mass == 0 else 1.0/mass
        self.can_move: bool = True

    def __repr__(self) -> str:
        string = "ID: " + str(self.particle_id) + "\t"
        string += "X: " + str(self.curr_pos) + "\t"
        string += "V:" + str(self.curr_pos - self.prev_pos) + "\t"
        string += "Attached:" + str([(p.particle_id, value)
                                     for p, value in self.attached_particles.items()])
        return string

    def attach(self, other_particle, constraint: float) -> None:
        if other_particle not in self.attached_particles:
            self.attached_particles[other_particle] = constraint
        # on the other side.
        if self not in other_particle.attached_particles:
            other_particle.attached_particles[self] = constraint


class Ball(Particle):
    mass: float = 1.0
    radius: float = 5.0

    def __init__(self, position: Tuple[float, float], velocity: Tuple[float, float]):
        super().__init__(position, Ball.mass)
        # setting the "velocity" by changing the previous position.
        self.prev_pos = self.curr_pos - \
            FRAME_TIME * np.asarray(velocity, float)

    def might_collide_with_wall(self) -> bool:
        return (self.curr_pos[0] - Ball.radius) - WALL_X < 5

    def might_collide_with_mountain(self) -> bool:
        ball_x, ball_y = self.curr_pos
        radius = Ball.radius
        return MOUNTAIN_X_MIN <= (ball_x + radius) and (ball_x - radius) <= MOUNTAIN_X_MAX \
            and MOUNTAIN_Y_MIN <= (ball_y + radius) and (ball_y - radius) <= MOUNTAIN_Y_MAX

    def draw(self) -> None:
        arcade.draw_circle_filled(
            *self.curr_pos, Ball.radius, arcade.color.BLACK)


class StickConstraint():
    def __init__(self, p1: Particle, p2: Particle, rest_length: float = None, relatice_tolerance: float = 0.10):
        """
        Creates a new stick constraint between two particles, keeping them apart
        with a distance of `rest_length` and with a tolerance of `relative_tolerance`.
        """
        self.p1 = p1
        self.p2 = p2
        if rest_length is None:
            self.rest_length = np.linalg.norm(self.p2.curr_pos - self.p1.curr_pos)
        else:
            self.rest_length = rest_length
        self.tolerance_rel = relatice_tolerance
        self.tolerance_abs = relatice_tolerance * self.rest_length
    
    def apply(self) -> None:
        """
        Applies the constraint, pushing the particles closer together or further appart.
        """
        delta = self.p2.curr_pos - self.p1.curr_pos
        distance = np.linalg.norm(delta)
        minimum = self.rest_length - self.tolerance_abs
        maximum = self.rest_length + self.tolerance_abs
        if distance < minimum:
            # the particles are too close together!
            error = (distance - minimum) / distance
            self.p1.curr_pos -= delta * 0.5 * error
            self.p2.curr_pos += delta * 0.5 * error
        elif distance > maximum:
            # the particles are too far from one another.
            error = (distance - maximum) / distance
            self.p1.curr_pos -= delta * 0.5 * error
            self.p2.curr_pos += delta * 0.5 * error


class RigidBody():
    particles: List[Particle]
    stick_constraints: List[StickConstraint]

class ParticleSystem():

    # number of iterations of the verlet integration portion.
    NUM_ITERATIONS: float = 1

    # changing the wind every 2 seconds. (0.5 seconds is a bit too fast!)
    wind_change_interval: int = FRAME_RATE * 2
    max_wind_speed: float = 15
    wind_speed: float = 5

    def __init__(self):
        self.balls: List[Ball] = []
        self.turkeys: List[turkey.Turkey] = []

        self.mountain_points: List[Point] = mountain_points

        # counter for the number of frames.
        self._i: int = 0

    def time_step(self) -> None:
        self.accumulate_forces()
        self.verlet()
        self.satisfy_constraints()
        # if self._i % ParticleSystem.wind_change_interval == 0:
        #     ParticleSystem.wind_speed = random.uniform(
        #         -ParticleSystem.max_wind_speed, ParticleSystem.max_wind_speed)
        #     print("Wind speed changed to ", ParticleSystem.wind_speed)
        self._i += 1

    def verlet(self) -> None:
        for p in filter(lambda p: p.can_move, self.balls):
            temp = np.copy(p.curr_pos)
            p.curr_pos += (p.curr_pos - p.prev_pos) + \
                p.acceleration * FRAME_TIME * FRAME_TIME
            p.prev_pos = temp

    def accumulate_forces(self) -> None:
        for ball in filter(lambda b: b.can_move, self.balls):
            if ball.curr_pos[1] >= WIND_START_Y:
                ball.acceleration = np.asarray(
                    (ParticleSystem.wind_speed, GRAVITY))
            else:
                ball.acceleration = np.asarray((0.0, GRAVITY))


    def satisfy_constraints(self) -> None:
        for i in range(ParticleSystem.NUM_ITERATIONS):
            for ball in filter(lambda ball: ball.can_move, self.balls):
                # if the ball hits the ground, it is dead.
                if (ball.curr_pos[1] - Ball.radius) <= GROUND_Y:
                    print("Ball collided with the ground!")
                    ball.can_move = False
                    continue

                if ball.might_collide_with_wall():
                    p1 = np.asarray((WALL_X, GROUND_Y))
                    p2 = np.asarray((WALL_X, SCREEN_HEIGHT - 1))
                    collision, wall_p, penetration_distance = circle_line_intersection(
                        ball.curr_pos, Ball.radius, p1, p2)
                    if collision:
                        print("Ball Collided with the wall!")
                        print(collision, wall_p, penetration_distance)
                        velocity = ball.curr_pos - ball.prev_pos
                        restitution_coefficient: float = 0.95
                        # Only the x-component of the velocity is changed (since the wall is vertical)
                        velocity[0] *= -1 * restitution_coefficient
                        # get the ball out of the wall by sliding it to the right.
                        ball.curr_pos[0] += penetration_distance
                        # set the ball's velocity.
                        ball.prev_pos = ball.curr_pos - velocity
                        # can't possibly collide with anything else at the same time.
                        continue

                elif ball.might_collide_with_mountain():
                    # check if the ball collidies with a line of the mountain.
                    for p0, p1 in pairs(self.mountain_points):
                        result = circle_line_intersection(
                            ball.curr_pos, Ball.radius, p0, p1)
                        collision, mountain_p, penetration_dist = result
                        if not collision:
                            continue
                        print("Ball Collided with the mountain!")
                        print(mountain_p, penetration_dist)

                        restitution_coefficient: float = 0.50
                        # the mountain segment is the tangential vector to the collision.
                        tangential = p1 - p0
                        tangential /= np.linalg.norm(tangential)
                        # the normal is perpendicular to the mountain segment.
                        # TODO: we want the upward-pointing normal, does this matter ?
                        normal = np.asarray(
                            (-tangential[1], tangential[0]), float)

                        # move the ball out of the mountain.
                        ball.curr_pos += normal * penetration_dist

                        velocity = ball.curr_pos - ball.prev_pos

                        v_tangent = np.dot(velocity, tangential)
                        v_normal = np.dot(velocity, normal)

                        # inelastic collision: the normal component is reversed.
                        v_normal *= -1 * restitution_coefficient
                        new_velocity = v_tangent * tangential + v_normal * normal
                        # set the ball's velocity
                        ball.prev_pos = ball.curr_pos - new_velocity
                        break
                min_constraint = (0, GROUND_Y)
                max_constraint = (SCREEN_WIDTH, SCREEN_HEIGHT)
                ball.curr_pos = np.max([ball.curr_pos, min_constraint], axis=0)
                ball.curr_pos = np.min([ball.curr_pos, max_constraint], axis=0)

            for turkey in self.turkeys:
                for constraint in turkey.stick_constraints:
                    pass

                for attached_p, constraint in p.attached_particles.items():
                    # Pseudo-code to satisfy (C2)
                    delta = p.curr_pos - attached_p.curr_pos
                    delta_dot = np.dot(delta, delta)
                    delta_length = np.sqrt(delta_dot)
                    diff = (delta_length-constraint)/delta_length
                    p.curr_pos -= delta*0.5*diff
                    attached_p.curr_pos += delta*0.5*diff

                # Pseudo-code for satisfying (C2) using sqrt approximation
                # rest_length = c.length
                # delta = c.p2.curr_pos - c.p1.curr_pos
                # delta*=rest_length*rest_length/(delta*delta+rest_length*rest_length)-0.5
                # c.p1.curr_pos -= delta
                # c.p2.curr_pos += delta

                # if c.p1.inv_mass == 0 and c.p2.inv_mass == 0:
                #     # the two particles are immovable.
                #     continue

                # # Pseudo-code to satisfy (C2) while taking mass into account.
                # p1, p2 = c.p1, c.p2
                # delta = p2.curr_pos - p1.curr_pos
                # deltalength = np.sqrt(np.dot(delta, delta))
                # diff = (deltalength - c.rest_length)
                # diff /= (deltalength * (p1.inv_mass + p2.inv_mass))
                # p1.curr_pos -= p1.inv_mass * delta * diff
                # p2.curr_pos += p2.inv_mass * delta * diff
