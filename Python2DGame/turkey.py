import arcade
import numpy as np
from typing import List, Tuple, Set
from utils import pairs
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

TURKEY_POINTS: Set = None
TURKEY_WIDTH: float = None
TURKEY_HEIGHT: float = None
TURKEY_RADIUS: float = None

DEFAULT_SCALE: float = 5.0


TURKEY_POINTS = list(set([p for segment in TURKEY_SEGMENTS for p in segment]))
TURKEY_WIDTH, TURKEY_HEIGHT = np.max(TURKEY_POINTS, axis=0) - np.min(TURKEY_POINTS, axis=0)
TURKEY_RADIUS = max((TURKEY_HEIGHT, TURKEY_WIDTH)) / 2
print("HERE")
if __name__ == "__main__":
    pass


def create_turkey(scale: float = DEFAULT_SCALE) -> arcade.ShapeElementList:
    turkey = arcade.ShapeElementList()
    color = arcade.color.BLACK
    for segment in TURKEY_SEGMENTS[:-1]:
        segment = np.asarray(segment, dtype=float)
        segment *= scale
        for p1, p2 in pairs(segment):
            turkey.append(arcade.create_line(*p1, *p2, color=color))
    eye_point = np.asarray(TURKEY_SEGMENTS[-1][0], dtype=float)
    eye_radius = 1
    eye_point *= scale
    eye_radius *= np.sqrt(scale)
    turkey.append(arcade.create_ellipse_filled_with_colors(eye_point[0], eye_point[1], width=eye_radius, height=eye_radius, inside_color=color, outside_color=color))
    return turkey

class Turkey():
    def __init__(self, scale: float = DEFAULT_SCALE):
        pass
        self.shape_element_list = create_turkey(scale)
