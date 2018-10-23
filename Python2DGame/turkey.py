import arcade
import numpy as np
from typing import List, Tuple, Set
from utils import pairs
import game
# from game import RigidBody, StickConstraint, Particle
# list of contiguous segments that form the basis of a turkey.
TURKEY_SEGMENTS: List[List[Tuple[float, float]]]= [
    [ # left leg
        (-2, 0),
        (-1, 2),
        (-1, 4),
        (0, 5),
    ],
    [ # right leg
        (0,0),
        (1, 2),
        (1, 4),
        (0,5),
    ],    
    [ # contour 
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
    [ # the eye.
        (-6, 10)
    ]
]

BASE_POINTS: Set = None
BASE_WIDTH: float = None
BASE_HEIGHT: float = None
BASE_RADIUS: float = None

DEFAULT_SCALE: float = 4.0

BASE_POINTS = np.asarray(list(set([p for segment in TURKEY_SEGMENTS for p in segment])), dtype=float)
BASE_WIDTH, BASE_HEIGHT = np.max(BASE_POINTS, axis=0) - np.min(BASE_POINTS, axis=0)
BASE_RADIUS = max((BASE_HEIGHT, BASE_WIDTH)) / 2


class Turkey(arcade.ShapeElementList, game.RigidBody):
    max_pacing_speed: float = 2.0

    def __init__(self, scale: float = DEFAULT_SCALE):
        super().__init__()
        self.points: List[Tuple[float,float]] = BASE_POINTS * scale
        self.make_turkey_shapelist(scale)
        self.width : float = BASE_WIDTH * scale
        self.height : float = BASE_HEIGHT * scale
        self.radius : float = BASE_RADIUS * scale
        self.pacing_speed : float = 0

    def random_change_pace(self) -> None:
        pass


    def make_turkey_shapelist(self, scale: float) -> None:
        color = arcade.color.BLACK
        for segment in TURKEY_SEGMENTS[:-1]:
            segment = np.asarray(segment, dtype=float)
            segment *= scale
            for p1, p2 in pairs(segment):
                self.append(arcade.create_line(*p1, *p2, color=color))
        eye_point = np.asarray(TURKEY_SEGMENTS[-1][0], dtype=float)
        eye_radius = 1
        eye_point *= scale
        eye_radius *= np.sqrt(scale)
        self.append(arcade.create_ellipse_filled_with_colors(eye_point[0], eye_point[1], width=eye_radius, height=eye_radius, inside_color=color, outside_color=color))