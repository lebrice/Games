"""
Simple collision detection engine.
"""
# from midpoint_bisection import Point
import numpy as np
from typing import Tuple
import shapely
from shapely.geometry import Point, LineString
def signed_area_triangle(p0, p1, p2):
    # (p1.x - p0.x) * (p2.y - p0.y) - (p2.x - p0.x) * (p1.y - p0.y)
    return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) *(p1[1] - p0[1])

def circle_line_intersection(
        center: Point,
        radius: float,
        p0: Point,
        p1: Point,
    ) -> Tuple[bool, Point, float]:
    """
    Determines if there is an intersection between the circle and the line, and there is one, returns the intersection point and the penetration distance.

    In the case where there is two intersection points, returns the point on the line which is closest to the circle's center.
    """
    center = np.asarray(center, dtype=float)
    radius = np.asarray(radius, dtype=float)
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    # print((np.max([p0, p1], axis=0) < center - radius))
    # print((np.min([p0, p1], axis=0) > center + radius))
    if (any((np.max([p0, p1], axis=0) < center - radius)) or
        any((np.min([p0, p1], axis=0) > center + radius))):
        # It is clearly impossible that the circle intersect the line.
        # print("HERE!")
        return False, None, None
    
    center = Point(center) # center
    circle = center.buffer(radius).boundary # radius
    line = LineString([p0, p1]) # line
    intersection = circle.intersection(line)
    if intersection.is_empty:
        return False, None, None
    intersect = intersection.centroid
    intersect = Point(round(intersect.x, 4), round(intersect.y, 4))

    return True, intersect, radius - intersect.distance(center)

def line_line_intersection(p0, p1, p2, p3) -> Tuple[bool, Point]:
    """
    Determines if the lines (p1 --- p2) and (p3 --- p4) intersect.
    """
    sat_abc = signed_area_triangle(p0, p1, p2)
    sat_abd = signed_area_triangle(p0, p1, p3)
    if (sat_abc * sat_abd) > 0:
        # SAT_abc and SAT_abd are of the same sign, therefore there is no collision!
        return False, None
    else:
        # Neat solution, but a bit slow:
        line1 = LineString([p0, p1])
        line2 = LineString([p2, p3])
        intersect = line1.intersection(line2)
        if intersect.is_empty:
            return False, None
        else:
            return True, intersect


        # # there might be a collision!
        # # Find the point of intersection:
        # # for example: (1,2), (2,3):
        # # slope = (3 - 2) / (2 - 1) = 1
        # # offset = (2 - 1 * 1) = 1
        # # y = slope * x + offset
        # # y = 1 * x + 1
        # # rearrange the line equation:
        # # 1x + -1y = -1

        # # y = slope_i * x + offset_i
        # # gets converted to:
        # # -offset_i = slope_i * x - 1 * y
        # if p0[0] == p1[0] or p2[0] == p3[0]:
        #     # p0-p1 or p2-p3 is a vertical line
        #     raise NotImplementedError("Vertical lines aren't currently supported.")
        # slope_a = (p1[1] - p0[1]) / (p1[0] - p0[0])
        # offset_a = (p0[1] - slope_a * p0[0])

        # slope_b = (p3[1] - p2[1]) / (p3[0] - p2[0])
        # offset_b = (p2[1] - slope_b * p2[0])

        # coefficients = np.array([
        #     [slope_a, -1],
        #     [slope_b, -1],
        # ])
        # constants = np.array([-offset_a, -offset_b])
        # # Find the point of intersection
        # x, y = np.linalg.solve(coefficients, constants)
        # # check that (x, y) is within on the line segment (p0, p1)
        # if slope_a >= 0:
        #     # check that the x of the solution point is within the range [p0.x, p1.x]
        #     if not (p0[0] <= x <= p1[0]):
        #         return False, None
        #     # check that the y of the solution point is within the range [p0.y, p1.y]
        #     if not (p0[1] <= y <= p1[1]):
        #         return False, None
        # else:
        #     # check that the x of the solution point is within the range [p1.x, p0.x]
        #     if not (p1[0] <= x <= p0[0]):
        #         return False, None
        #     # check that the y of the solution point is within the range [p1.y, p0.y]
        #     if not (p1[1] <= y <= p0[1]):
        #         return False, None

        # # might not be important ? (not sure...)
        # # # check that (x, y) is within the line segment (p2, p3)
        # # if slope_b >= 0:
        # #     # check that the x of the solution point is within the range [p2.x, p3.x]
        # #     if not (p2[0] <= x <= p3[0]):
        # #         return False, None
        # #     # check that the y of the solution point is within the range [p2.y, p3.y]
        # #     if not (p2[1] <= y <= p3[1]):
        # #         return False, None
        # # else:
        # #     # check that the x of the solution point is within the range [p3.x, p2.x]
        # #     if not (p3[0] <= x <= p2[0]):
        # #         return False, None
        # #     # check that the y of the solution point is within the range [p3.y, p2.y]
        # #     if not (p3[1] <= y <= p2[1]):
        # #         return False, None
        # return True, (x, y)
        
from timeit import default_timer as timer
from contextlib import contextmanager


@contextmanager
def time_this(times):
    start = timer()
    yield
    end = timer()
    times.append(end - start)

def main():
    # intersect, point = line_line_intersection((0, 0), (5, 0), (4, 2), (4, 1))
    # print(intersect, point)
    print("Just testing out the speed of collision detection.")
    times = []
    for _ in range(100):
        p0 = np.random.uniform(0, 10, size=(2))
        p1 = np.random.uniform(0, 10, size=(2))
        p2 = np.random.uniform(0, 10, size=(2))
        p3 = np.random.uniform(0, 10, size=(2))
        with time_this(times):
            intersect, point = line_line_intersection(p0, p1, p2, p3)
    print(np.mean(times))
    times = []

    for i in range(100):
        center = np.random.uniform(0, 10, size=(2))
        radius = np.random.uniform(0, 3)
        p1 = np.random.uniform(0, 10, size=(2))
        p2 = np.random.uniform(0, 10, size=(2))

        with time_this(times):
            intersect, point, distance = circle_line_intersection(center, radius, p1, p2)
    # print(intersect, point, distance)
    print(np.mean(times))

if __name__ == '__main__':
    main()

