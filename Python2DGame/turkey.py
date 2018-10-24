import arcade
import numpy as np
from typing import List, Tuple, Set, Dict

import game
from utils import pairs
from physics import RigidBody, Particle, StickConstraint
# from game import RigidBody, StickConstraint, Particle
# list of contiguous segments that form the basis of a turkey.
TURKEY_SEGMENTS: Dict[str, List[Tuple[float, float]]] = {
    "left_leg": [
        (-2, 0),
        (-1, 2),
        (-1, 4),
        (0, 5),
    ],
    "right_leg": [
        (0,0),
        (1, 2),
        (1, 4),
        (0,5),
    ],
    "contour" : [ 
        (0,5),
        (1,4),
        (2,5),
        (4,5),
        (6,7),
        (6,8),
        (7,9),
        (5,9),
        (6,10),
        (5,11),
        (4,9),
        (2,10),
        (-1,10),
        (-3, 9),
        (-4, 8),
        (-4, 9),
        (-5, 11),
        (-6, 11),
        (-8, 10),
        (-7, 9),
        (-7, 7),
        (-6, 9),
        (-6, 7),
        (-5, 6),
        (-2, 5),
        (-1, 4),
        (0,5),
    ],
    "eye": [
        (-6, 10)
    ]
}

BASE_POINTS: Set = None
BASE_WIDTH: float = None
BASE_HEIGHT: float = None
BASE_RADIUS: float = None

DEFAULT_SCALE: float = 4.0

BASE_POINTS = np.asarray(list(set([p for segment in TURKEY_SEGMENTS.values() for p in segment])), dtype=float)
BASE_WIDTH, BASE_HEIGHT = np.max(BASE_POINTS, axis=0) - np.min(BASE_POINTS, axis=0)
BASE_RADIUS = max((BASE_HEIGHT, BASE_WIDTH)) / 2


class Turkey(RigidBody):
    max_pacing_speed: float = 2
    color = arcade.color.BLACK
    jump_impulse_speed: float = 10
    # the mass of each particle that makes up a Turkey
    mass: float = 0.1
    def __init__(self, scale: float = DEFAULT_SCALE):
        super().__init__()
        self.scale = scale
        self.segments: Dict[str, List[Particle]] = {}
        # self.make_turkey_shapelist(self.scale)
        self.width : float = BASE_WIDTH * self.scale
        self.height : float = BASE_HEIGHT * self.scale
        self.radius : float = BASE_RADIUS * self.scale
        self.pacing_speed : float = 0

        self._create_particles_and_constraints()


    def _create_particles_and_constraints(self) -> None:
        for name, segment in TURKEY_SEGMENTS.items():
            # scale the points up.
            scaled_points = np.asarray(segment, float) * self.scale
            self.segments[name] = []
            for p in scaled_points:
                # find the particle if it already exists, otherwise create a new one.
                particle: Particle = next(
                    (part for part in self.particles if np.allclose(part.curr_pos, p)),
                    Particle(position=p, mass=Turkey.mass)
                )
                if particle not in self.particles:
                    self.particles.append(particle)
                # print("adding a new particle at ", particle.curr_pos)
                # print(len(self.particles))
                # append the particle to this segment.
                self.segments[name].append(particle)
            
            if name == "eye":
                continue

            # create a Stick constraint for each pair within this segment.
            for p1, p2 in pairs(self.segments[name]):
                constraint = StickConstraint(p1, p2, relatice_tolerance=0.1)
                self.stick_constraints.append(constraint)

            # add more flexible stick constraints between every other node on this segment:
            for p1, p2 in pairs(self.segments[name][::2]):
                constraint = StickConstraint(p1, p2, relatice_tolerance=0.4)
                self.stick_constraints.append(constraint)


    def jump(self) -> None:
        """jumps by setting the y velocity of all particles to a given value."""
        print("Jumping!")
        self.velocity += np.asarray((0.0, Turkey.jump_impulse_speed))

    def move(self, change_x: float, change_y: float) -> None:
        """Moves the turkey by a certain amount (all particles), then sets the speed to 0."""
        # print(change_x, change_y)
        change = np.asarray((change_x, change_y), float)
        for particle in self.particles:
            particle.curr_pos += change
            particle.velocity = 0
    

    @property
    def velocity(self) -> Tuple[float, float]:
        """The average velocity of all the particles of the Turkey."""
        return np.mean([p.velocity for p in self.particles], axis=0)

    @velocity.setter
    def velocity(self, value: Tuple[float, float]) -> None:
        """Gives a velocity to all the particles at the same time."""
        for p in self.particles:
            p.velocity = value


    def draw(self) -> None:
        segments = [segment for name, segment in self.segments.items() if name != "eye"]
        for segment in segments:
            points = [p.curr_pos for p in segment]   
            arcade.draw_line_strip(points, Turkey.color, 2)
        eye_pos = self.segments["eye"][0].curr_pos
        arcade.draw_circle_filled(*eye_pos, self.scale / 2, color=Turkey.color)

    # def make_turkey_shapelist(self, scale: float) -> None:
    #     """
    #     NOT USED:
    #     This creates a render-only (non-physics object).
    #     """
    #     color = arcade.color.BLACK
    #     for segment in TURKEY_SEGMENTS.values():
    #         segment = np.asarray(segment, dtype=float)
    #         segment *= scale
    #         for p1, p2 in pairs(segment):
    #             self.append(arcade.create_line(*p1, *p2, color=color))
    #     eye_point = np.asarray(TURKEY_SEGMENTS["eye"][0], dtype=float)
    #     eye_radius = 1
    #     eye_point *= scale
    #     eye_radius *= np.sqrt(scale)
    #     self.append(arcade.create_ellipse_filled_with_colors(eye_point[0], eye_point[1], width=eye_radius, height=eye_radius, inside_color=color, outside_color=color))