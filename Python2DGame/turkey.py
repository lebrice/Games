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


class Turkey(arcade.ShapeElementList, RigidBody):
    max_pacing_speed: float = 2.0
    color = arcade.color.BLACK
    # the mass of each particle that makes up a Turkey
    mass: float = 0.1
    def __init__(self, scale: float = DEFAULT_SCALE):
        super().__init__()
        self.scale = scale

        self.particles = []
        self.segments: Dict[str, List[Particle]] = {}

        for name, segment in TURKEY_SEGMENTS.items():
            # scale the points up.
            scaled_points = np.asarray(segment, float) * self.scale
            self.segments[name] = []
            for p in scaled_points:
                particle = Particle(position=p, mass=Turkey.mass)
                # if particle in self.particles:
                self.particles.append(particle)
                self.segments[name].append(particle)
            



        print(self.segments)


        self.make_turkey_shapelist(self.scale)
        self.width : float = BASE_WIDTH * self.scale
        self.height : float = BASE_HEIGHT * self.scale
        self.radius : float = BASE_RADIUS * self.scale
        self.pacing_speed : float = 0

    def random_change_pace(self) -> None:
        pass

    # def draw(self) -> None:
    #     pass

    def make_turkey_shapelist(self, scale: float) -> None:
        color = arcade.color.BLACK
        for segment in TURKEY_SEGMENTS.values():
            segment = np.asarray(segment, dtype=float)
            segment *= scale
            for p1, p2 in pairs(segment):
                self.append(arcade.create_line(*p1, *p2, color=color))
        eye_point = np.asarray(TURKEY_SEGMENTS["eye"][0], dtype=float)
        eye_radius = 1
        eye_point *= scale
        eye_radius *= np.sqrt(scale)
        self.append(arcade.create_ellipse_filled_with_colors(eye_point[0], eye_point[1], width=eye_radius, height=eye_radius, inside_color=color, outside_color=color))