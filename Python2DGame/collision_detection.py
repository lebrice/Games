"""
Simple collision detection engine.
"""
from midpoint_bisection import Point
import numpy as np
from typing import Tuple

def signed_area_triangle(p0, p1, p2):
    # (p1.x - p0.x) * (p2.y - p0.y) - (p2.x - p0.x) * (p1.y - p0.y)
    return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) *(p1[1] - p0[1])

def line_line_intersection(p0, p1, p2, p3) -> Tuple[bool, Tuple[float, float]]
    """
    Determines if the lines (p1 --- p2) and (p3 --- p4) intersect.
    """
    sat_abc = signed_area_triangle(p0, p1, p2)
    sat_abd = signed_area_triangle(p0, p1, p3)
    if (sat_abc * sat_abd) > 0:
        # SAT_abc and SAT_abd are of the same sign, therefore there is no collision!
        return False, None
    else:
        # there might be a collision!
        # Find the point of intersection:
        # for example: (1,2), (2,3):
        # slope = (3 - 2) / (2 - 1) = 1
        # offset = (2 - 1 * 1) = 1
        # y = slope * x + offset
        # y = 1 * x + 1 
        # Therefore giving:
        # 1x + -1y = -1


        # y = slope_i * x + offset_i
        # gets converted to:
        # -offset_i = slope_i * x - 1 * y
        slope_a = (p1[1] - p0[1]) / (p1[0] - p0[0])
        offset_a = (p0[1] - slope_a * p0[0])

        slope_b = (p3[1] - p2[1]) / (p3[0] - p2[0])
        offset_b = (p2[1] - slope_b * p2[0])

        coefficients = np.array([
            [slope_a, -1],
            [slope_b, -1],
        ])
        constants = np.array([-offset_a, -offset_b])
        # Find the point of intersection
        x, y = np.linalg.solve(coefficients, constants)
        # check that (x, y) is within on the line segment (p0, p1)
        if slope_a >= 0:
            # check that the x of the solution point is within the range [p0.x, p1.x]
            if not (p0[0] <= x <= p1[0]):
                return False, None
            # check that the y of the solution point is within the range [p0.y, p1.y]
            if not (p0[1] <= y <= p1[1]):
                return False, None
        else:
            # check that the x of the solution point is within the range [p1.x, p0.x]
            if not (p1[0] <= x <= p0[0]):
                return False, None
            # check that the y of the solution point is within the range [p1.y, p0.y]
            if not (p1[1] <= y <= p0[1]):
                return False, None

        # might not be important ? (not sure...)
        # # check that (x, y) is within the line segment (p2, p3)
        # if slope_b >= 0:
        #     # check that the x of the solution point is within the range [p2.x, p3.x]
        #     if not (p2[0] <= x <= p3[0]):
        #         return False, None
        #     # check that the y of the solution point is within the range [p2.y, p3.y]
        #     if not (p2[1] <= y <= p3[1]):
        #         return False, None
        # else:
        #     # check that the x of the solution point is within the range [p3.x, p2.x]
        #     if not (p3[0] <= x <= p2[0]):
        #         return False, None
        #     # check that the y of the solution point is within the range [p3.y, p2.y]
        #     if not (p3[1] <= y <= p2[1]):
        #         return False, None

        # the point is on one of the lines. All is good.
        return True, (x, y)

def main():
    intersect, point = line_line_intersection((0, 0), (5, 0), (5.5, 5), (4.9, 0.1))
    print(intersect, point)

if __name__ == '__main__':
    main()

