from typing import NamedTuple, List, Tuple, Set, Dict
from midpoint_bisection import Point
import numpy as np
import random
import testing
import os
import arcade
from enum import Enum
# from testing import SCREEN_HEIGHT, SCREEN_WIDTH, GROUND_Y, WALL_X
import collision_detection

class ParticleType(Enum):
    ball = 0
    cloud = 1
    wall = 2
    mountain = 3
    turkey = 4

class Particle():
    next_particle_id = 0
    def __hash__(self):
        return hash(self.particle_id)
    
    def __eq__(self, other: object):
        if other.__class__ == self.__class__:
            return other.particle_id == self.particle_id
        return NotImplemented

    def __init__(self, p_type: ParticleType, position: Tuple[float, float], mass: float = 0):
        self.particle_id = Particle.next_particle_id
        Particle.next_particle_id += 1
        self.curr_pos = np.asarray(position, dtype=float)
        self.prev_pos = np.asarray(position, dtype=float)
        self.acceleration = np.zeros(2, float)
        self.attached_particles: Dict[Particle, float] = dict()
        self.inv_mass = 0 if mass == 0 else 1.0/mass
        self.particle_type: ParticleType = p_type

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

    def get_forces(self) -> Tuple[float, float]:
        return (0.0, 0.0)


class Cloud(arcade.Sprite):
    filename: str = os.path.join("images", "cloud_sprite.png")
    scale: float = 0.1
    def __init__(self, position: Tuple[float, float]):
        super().__init__(
            filename=Cloud.filename,
            scale=Cloud.scale,
            center_x = position[0],
            center_y = position[1],
        )

    def update(self) -> None:
        self.change_x = ParticleSystem.wind_speed * FRAME_TIME
        self.center_x += self.change_x
        
        if self.right < 0:
            # wrap around to the right of the screen.
            self.right = SCREEN_WIDTH - 1 + self.width
        
        if self.left > SCREEN_WIDTH - 1:
            self.left = - self.width
        
        # if self.left < 0:
        #     self.left = 0
        # elif self.right > SCREEN_WIDTH - 1:
        #     self.right = SCREEN_WIDTH - 1


    

class Ball(Particle):
    mass : float = 1.0
    radius: float = 5.0
    def __init__(self, position: Tuple[float, float], velocity: Tuple[float, float]):
        super().__init__(ParticleType.ball, position, Ball.mass)
        # setting the "velocity" by changing the previous position.
        self.prev_pos = self.curr_pos - FRAME_TIME * np.asarray(velocity, float)



class StickConstraint(NamedTuple):
    p1: Particle
    p2: Particle
    rest_length: float

class ParticleSystem():
    # changing the wind every 2 seconds. (0.5 seconds is a bit too fast!)
    wind_change_interval: int = FRAME_RATE * 2
    max_wind_speed : float = 15
    wind_speed : float = 0

    def __init__(self):
        self.particles: List[Particle] = []
        self.constraints: List[StickConstraint] = []
        # counter for the number of frames.
        self._i: int = 0

    def time_step(self) -> None:
        self.accumulate_forces()
        self.verlet()
        self.satisfy_constraints()
        if self._i % ParticleSystem.wind_change_interval == 0:
            ParticleSystem.wind_speed = random.uniform(-ParticleSystem.max_wind_speed, ParticleSystem.max_wind_speed)
            print("Wind speed changed to ", ParticleSystem.wind_speed)
        self._i += 1

    def verlet(self) -> None:
        for p in self.particles:
            temp = np.copy(p.curr_pos)
            p.curr_pos += (p.curr_pos - p.prev_pos) + p.acceleration * FRAME_TIME * FRAME_TIME
            p.prev_pos = temp


    def accumulate_forces(self) -> None:
        p: Particle
        for p in self.particles:
            if p.particle_type == ParticleType.ball:
                if p.curr_pos[1] >= WIND_START_Y:
                    p.acceleration = np.asarray((ParticleSystem.wind_speed, GRAVITY))
                else:
                    p.acceleration = np.asarray((0.0, GRAVITY))

    def ball_might_collide_with_wall(self, ball: Ball) -> bool:
        return (ball.curr_pos[0] - Ball.radius) - WALL_X < 5

    def ball_might_collide_with_mountain(self, ball: Ball) -> bool:
        return (ball.curr_pos[0])

    def satisfy_constraints(self) -> None:
        for i in range(NUM_ITERATIONS):
            p: Particle
            for p in self.particles:

                if p.particle_type == ParticleType.ball:
                    if ball_might_collide_with_wall(p):
                        wall_point, ball_point = collision_detection.circle_line_intersection(p.curr_pos, Ball.radius)



                    # constrain #1: the particles have to stay within the area.
                    min_constraint = (0, GROUND_Y)
                    max_constraint = (SCREEN_WIDTH, SCREEN_HEIGHT)
                    p.curr_pos = np.max([p.curr_pos, min_constraint], axis=0)
                    p.curr_pos = np.min([p.curr_pos, max_constraint], axis=0)



            for c in self.constraints:
                # Pseudo-code for satisfying (C2) using sqrt approximation
                # rest_length = c.length
                # delta = c.p2.curr_pos - c.p1.curr_pos
                # delta*=rest_length*rest_length/(delta*delta+rest_length*rest_length)-0.5
                # c.p1.curr_pos -= delta
                # c.p2.curr_pos += delta

                if c.p1.inv_mass == 0 and c.p2.inv_mass == 0:
                    # the two particles are immovable.
                    continue

                # Pseudo-code to satisfy (C2) while taking mass into account.
                p1, p2 = c.p1, c.p2
                delta = p2.curr_pos - p1.curr_pos
                deltalength = np.sqrt(np.dot(delta, delta))
                diff = (deltalength - c.rest_length)
                diff /= (deltalength * (p1.inv_mass + p2.inv_mass))
                p1.curr_pos -= p1.inv_mass * delta * diff
                p2.curr_pos += p2.inv_mass * delta * diff

                # for attached_p, constraint in p.attached_particles.items():
                #     # Pseudo-code to satisfy (C2)

                #     delta = p.curr_pos - attached_p.curr_pos
                #     delta_dot = np.dot(delta, delta)
                #     delta_length = np.sqrt(delta_dot)
                #     diff = (delta_length-constraint)/delta_length
                #     p.curr_pos -= delta*0.5*diff
                #     attached_p.curr_pos += delta*0.5*diff

# def main():
#     p1 = Particle([0, 11])
#     p2 = Particle([0, 1])
#     p1.attach(p2, 10)
#     particleSystem = ParticleSystem()
#     particleSystem.particles.append(p1)
#     particleSystem.particles.append(p2)
#     for i in range(5):
#         print("----- iteration ", i, "-------")
#         particleSystem.time_step()
#         for p in particleSystem.particles:
#             print(p)


# if __name__ == '__main__':
#     main()
