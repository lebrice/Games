from midpoint_bisection import midpoint_bisection
import numpy as np

FRAME_RATE = 30
FRAME_TIME = 1.0 / FRAME_RATE

GRAVITY = -9.81

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_Y = SCREEN_HEIGHT / 6
MOUNTAIN_WIDTH = SCREEN_WIDTH / 3
# starting coordinates of the mountain, before midpoint bijection.
MOUNTAIN_START_X = SCREEN_WIDTH / 3
MOUNTAIN_START_Y = SCREEN_HEIGHT / 2
MOUNTAIN_END_X = MOUNTAIN_START_X + MOUNTAIN_WIDTH
MOUNTAIN_END_Y = GROUND_Y
MOUNTAIN_HEIGHT = MOUNTAIN_END_Y - MOUNTAIN_END_Y
WALL_X = 0
mountain_base_points = [
    (MOUNTAIN_START_X, GROUND_Y),
    (MOUNTAIN_START_X + MOUNTAIN_WIDTH // 2, SCREEN_HEIGHT // 2),
    (MOUNTAIN_END_X, GROUND_Y),
]
CANNON_X = SCREEN_WIDTH * 7/8
CANNON_Y = GROUND_Y + 10
CLOUD_Y = (7/8) * SCREEN_HEIGHT

mountain_points = midpoint_bisection(mountain_base_points, max_iterations=4)
MOUNTAIN_X_MAX, MOUNTAIN_Y_MAX = np.max(mountain_points, axis=0)
MOUNTAIN_X_MIN, MOUNTAIN_Y_MIN = np.min(mountain_points, axis=0)
WIND_START_Y: int = MOUNTAIN_Y_MAX