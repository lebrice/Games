"""
Module for midpoint bisection
"""

from typing import List, NamedTuple, Iterable, Iterator, Tuple
import random
import numpy as np
from itertools import cycle, islice
from utils import pairs



def main():
    points = [
        (0, 0),
        (50, 50),
        (65, 50),
        (100, 0),
    ]
    new_points = midpoint_bisection(points, max_iterations=3)
    print(new_points[:,1])


def interlace(list1: List, list2: List) -> List:
    """
    Interlaces the two lists to create a new list.
    
    `interlace([a,b,c], [x,y,z]) -> [a,x,b,y,c,z]`
    `interlace([a,b,c], [x,y]) -> [a,x,b,y,c]`
    """
    result = [None] * (len(list1) + len(list2))
    result[::2] = list1
    result[1::2] = list2
    return result

def midpoint_bisection(points: List[Tuple[float, float]], max_iterations=4, iteration: int = 0) -> List[Tuple[float, float]]:
    """
    """
    points = np.asarray(points, float)
    def midpoint(point1: Tuple[float, float], point2: Tuple[float, float], displacement_range: float, iteration: int = 0) -> Tuple[float, float]:
        mean_y = (point1[1] + point2[1]) / 2
        mean_x = (point1[0] + point2[0]) / 2

        random_displacement = np.random.normal(scale=0.5) * displacement_range
        random_displacement *= 2 ** (-iteration)
        
        return (
            mean_x,
            mean_y + random_displacement,
        )

    displacement_range = (max(points[:,1]) - min(points[:,1])) / 2
    
    def make_midpoints(points: List[Tuple[float, float]], displacement_range: float, iteration: int) -> List[Tuple[float, float]]:
        """
        Recursive function which actually makes the midpoints.
        """
        if iteration >= max_iterations:
            return points
        points_to_add = [
            midpoint(p1, p2, displacement_range, iteration) for p1, p2 in pairs(points)
        ]
        result_points = interlace(points, points_to_add)
        del points, points_to_add
        return make_midpoints(result_points, displacement_range, iteration + 1)

    return np.asarray(make_midpoints(points, displacement_range, 0), float)

if __name__ == "__main__":
    main()