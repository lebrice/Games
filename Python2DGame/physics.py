from typing import NamedTuple, List, Tuple, Set, Dict
from midpoint_bisection import Point
import numpy as np

FRAME_RATE = 30
FRAME_TIME = 1.0 / FRAME_RATE

GRAVITY = -9.81

NUM_ITERATIONS = 1

AREA_WIDTH = 1000
AREA_HEIGHT = 1000


class Particle():
    particle_id = 0

    def __init__(self, position: Tuple[float, float], mass: float = 0):
        self.particle_id = Particle.particle_id
        Particle.particle_id += 1
        self.curr_pos = np.asarray(position, dtype=float)
        self.prev_pos = np.asarray(position, dtype=float)
        self.acceleration = np.array([0, 0], dtype=float)
        self.attached_particles: Dict[Particle, float] = dict()
        self.inv_mass = 0 if mass == 0 else 1.0/mass

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


class StickConstraint():
    def __init__(self, particle1: Particle, particle2: Particle, rest_length: float):
        self.p1 = particle1
        self.p2 = particle2
        self.rest_length = rest_length


class ParticleSystem():
    def __init__(self, particles: List[Particle]):
        self.particles: List[Particle] = particles
        self.constraints: List[StickConstraint] = []

    def time_step(self) -> None:
        self.accumulate_forces()
        self.verlet()
        self.satisfy_constraints()

    def verlet(self) -> None:
        for p in self.particles:
            temp = p.curr_pos
            p.curr_pos += (p.curr_pos - p.prev_pos) + \
                p.acceleration * FRAME_TIME * FRAME_TIME
            # p.curr_pos[0] += (p.curr_pos[0] - p.prev_pos[0]) + p.acceleration[0] * FRAME_TIME * FRAME_TIME
            # p.curr_pos[1] += (p.curr_pos[1] - p.prev_pos[1]) + p.acceleration[1] * FRAME_TIME * FRAME_TIME
            p.prev_pos = temp

    def accumulate_forces(self) -> None:
        for p in self.particles:
            p.acceleration = np.asarray((0, GRAVITY), dtype=float)

    def satisfy_constraints(self) -> None:
        for i in range(NUM_ITERATIONS):
            for p in self.particles:
                # constrain #1: the particles have to stay within the area.
                min_constraint = (0, 0)
                max_constraint = (AREA_WIDTH, AREA_HEIGHT)
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


def main():
    p1 = Particle([0, 11])
    p2 = Particle([0, 1])
    p1.attach(p2, 10)
    particleSystem = ParticleSystem([p1, p2])
    for i in range(5):
        print("----- iteration ", i, "-------")
        particleSystem.time_step()
        for p in particleSystem.particles:
            print(p)


if __name__ == '__main__':
    main()
