import arcade
import numpy as np
from typing import NamedTuple, List, Tuple, Set, Dict
import numpy as np
import random
import os
import arcade
import math
from enum import Enum
import collision_detection
from collision_detection import circle_line_intersection
from midpoint_bisection import midpoint_bisection
import turkey

# from turkey import Turkey
from utils import pairs
FRAME_RATE = 30
FRAME_TIME = 1.0 / FRAME_RATE

GRAVITY = -9.81

NUM_ITERATIONS = 1

# Set the working directory (where we expect to find files) to the same
# directory this .py file is in. You can leave this out of your own
# code, but it is needed to easily run the examples using "python -m"
# as mentioned at the top of this program.
file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)
IMAGE_DIR = os.path.join(os.path.curdir, "images")

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
mountain_points = midpoint_bisection(mountain_base_points, max_iterations=4)
MOUNTAIN_X_MAX, MOUNTAIN_Y_MAX = np.max(mountain_points, axis=0)
MOUNTAIN_X_MIN, MOUNTAIN_Y_MIN = np.min(mountain_points, axis=0)
CANNON_X = SCREEN_WIDTH * 7/8
CANNON_Y = GROUND_Y + 10
CLOUD_Y = (7/8) * SCREEN_HEIGHT

WIND_START_Y: int = MOUNTAIN_Y_MAX

class Mountain(arcade.ShapeElementList):
    def __init__(self):
        super().__init__()
        for p1, p2 in pairs(mountain_points):
            bottom_left = (p1[0], GROUND_Y)
            bottom_right = (p2[0], GROUND_Y)
            points_list = [
                bottom_left,
                p1,
                p2,
                bottom_right,
            ]
            # each "segment" of the mountain is a convex polygon.
            self.append(arcade.create_polygon(points_list, arcade.color.BROWN_NOSE))

class MyGame(arcade.Window):
    # Frame counter.
    i: int

    def __init__(self, width, height):
        super().__init__(width, height)
        MyGame.i = 0
        # If you have sprite lists, you should create them here,
        # and set them to None
        self.wall_points = [
            (WALL_X, GROUND_Y),
            (WALL_X, SCREEN_HEIGHT - 1),
        ]
        self.turkeys: List[arcade.ShapeElementList] = []
        self.particle_system: ParticleSystem = None
        self.ball = None
        self.clouds: arcade.SpriteList = None
        self.cannon_angle: float = 0.
        self.mountain: Mountain = None

    def setup(self):
        # Create your sprites and sprite lists here
        self.mountain = Mountain()
        self.particle_system = ParticleSystem()
        self.particle_system.mountain_points = mountain_points
        self.clouds = arcade.SpriteList()
        self.clouds.append(Cloud((SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2/3)))
        self.clouds.append(Cloud((SCREEN_WIDTH / 3, SCREEN_HEIGHT * 3/4)))
        self.turkeys.append(turkey.Turkey())
        self.turkeys[0].move(100, 100)

    def on_draw(self):
        """
        Render the screen.
        """
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()
        self.draw_background()
        self.mountain.draw()
        self.draw_wall()
        if self.ball:
            self.ball.draw()
        self.clouds.draw()
        self.draw_cannon()
        self.draw_turkeys()
        # Call draw() on all your sprite lists below

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.clouds.update()
        self.particle_system.time_step()
        self.move_turkeys()
        MyGame.i += 1
        pass

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == arcade.key.DOWN:
            self.cannon_angle -= 5
            self.cannon_angle = max(self.cannon_angle, 0)
        if key == arcade.key.UP:
            self.cannon_angle += 5
            self.cannon_angle = min(self.cannon_angle, 90)
        if key == arcade.key.SPACE:
            self.fire_cannonball()

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass

    def draw_background(self):
        """
        This function draws the background. Specifically, the sky and ground.
        """
        # Draw the ground
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, GROUND_Y / 2,
                                     SCREEN_WIDTH - 1, GROUND_Y,
                                     arcade.color.DARK_SPRING_GREEN)
        # Draw the sky
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, GROUND_Y + (SCREEN_HEIGHT - GROUND_Y) / 2,
                                     SCREEN_WIDTH - 1, SCREEN_HEIGHT - GROUND_Y,
                                     arcade.color.SKY_BLUE)

    def draw_turkeys(self) -> None:
        """
        Draws the turkeys.
        """
        for turkey in self.turkeys:
            turkey.draw()

    def move_turkeys(self) -> None:
        """
        moves the turkeys a little bit at random.
        """
        def random_speed():
            return np.random.uniform(turkey.Turkey.max_pacing_speed, turkey.Turkey.max_pacing_speed)

        for t in self.turkeys:
            if MyGame.i % random.randint(1, 3 * FRAME_RATE) == 0:
                t.pacing_speed = random_speed()
            # TODO: only move the turkeys like this if they are below the wind ?
            if t.center_x - t.radius <= WALL_X:
                # we want to force the turkey to move right
                t.pacing_speed = abs(t.pacing_speed)
            elif t.center_x + t.radius >= MOUNTAIN_X_MIN:
                # we want to force the turkey to move left
                t.pacing_speed *= - abs(t.pacing_speed)
            t.move(t.pacing_speed, 0)

    def draw_wall(self):
        """Draws the wall on the left side of the screen."""
        arcade.draw_line(
            *self.wall_points[0], *self.wall_points[1], arcade.color.BLACK, 10)


    def draw_cannon(self) -> None:
        arcade.draw_rectangle_filled(
            CANNON_X, CANNON_Y, 10, 50, arcade.color.BLACK, 90 - self.cannon_angle)

    def fire_cannonball(self) -> None:
        if self.ball is not None:
            self.particle_system.balls.remove(self.ball)
            del self.ball
        print("Firing a new cannonball!")
        print("Cannon angle:", self.cannon_angle)
        magnitude = 85
        # the angle is defined from the left-horizontal, growing in clockwise
        # fashion until the vertical, at 90 degrees.
        x_component = magnitude * np.cos(np.deg2rad(self.cannon_angle)) * -1
        y_component = magnitude * np.sin(np.deg2rad(self.cannon_angle))
        velocity = (x_component, y_component)
        print(velocity)
        self.ball = Ball((CANNON_X, CANNON_Y), velocity)
        self.particle_system.balls.append(self.ball)

class Particle():
    next_particle_id = 0

    def __hash__(self):
        return hash(self.particle_id)

    def __eq__(self, other: object):
        if other.__class__ == self.__class__:
            return other.particle_id == self.particle_id
        return NotImplemented

    def __init__(self, position: Tuple[float, float], mass: float = 0):
        self.particle_id = Particle.next_particle_id
        Particle.next_particle_id += 1
        self.curr_pos = np.asarray(position, dtype=float)
        self.prev_pos = np.asarray(position, dtype=float)
        self.acceleration = np.zeros(2, float)
        self.attached_particles: Dict[Particle, float] = dict()
        self.inv_mass = 0 if mass == 0 else 1.0/mass
        self.can_move: bool = True

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


class Cloud(arcade.Sprite):
    filename: str = os.path.join("images", "cloud_sprite.png")
    scale: float = 0.1
    def __init__(self, position: Tuple[float, float]):
        super().__init__(
            filename=Cloud.filename,
            scale=Cloud.scale,
            center_x=position[0],
            center_y=position[1],
        )

    def update(self) -> None:
        self.change_x = ParticleSystem.wind_speed * FRAME_TIME
        self.center_x += self.change_x

        if self.right < 0:
            # wrap around to the right of the screen.
            self.right = SCREEN_WIDTH - 1 + self.width

        if self.left > SCREEN_WIDTH - 1:
            self.left = - self.width


class Ball(Particle):
    mass: float = 1.0
    radius: float = 5.0

    def __init__(self, position: Tuple[float, float], velocity: Tuple[float, float]):
        super().__init__(position, Ball.mass)
        # setting the "velocity" by changing the previous position.
        self.prev_pos = self.curr_pos - FRAME_TIME * np.asarray(velocity, float)

    def might_collide_with_wall(self) -> bool:
        return (self.curr_pos[0] - Ball.radius) - WALL_X < 5

    def might_collide_with_mountain(self) -> bool:
        ball_x, ball_y = self.curr_pos
        radius = Ball.radius
        return MOUNTAIN_X_MIN <= (ball_x + radius) and (ball_x - radius) <= MOUNTAIN_X_MAX \
            and MOUNTAIN_Y_MIN <= (ball_y + radius) and (ball_y - radius) <= MOUNTAIN_Y_MAX

    def draw(self) -> None:
        arcade.draw_circle_filled(*self.curr_pos, Ball.radius, arcade.color.BLACK)


class StickConstraint(NamedTuple):
    p1: Particle
    p2: Particle
    rest_length: float


class RigidBody():
    particles: List[Particle]
    stick_constraints: List[StickConstraint]


class ParticleSystem():
    # changing the wind every 2 seconds. (0.5 seconds is a bit too fast!)
    wind_change_interval: int = FRAME_RATE * 2
    max_wind_speed: float = 15
    wind_speed: float = 5

    def __init__(self):
        self.balls: List[Ball] = []
        self.turkeys: List[turkey.Turkey] = []

        self.mountain_points: List[Point] = mountain_points

        # counter for the number of frames.
        self._i: int = 0

    def time_step(self) -> None:
        self.accumulate_forces()
        self.verlet()
        self.satisfy_constraints()
        # if self._i % ParticleSystem.wind_change_interval == 0:
        #     ParticleSystem.wind_speed = random.uniform(
        #         -ParticleSystem.max_wind_speed, ParticleSystem.max_wind_speed)
        #     print("Wind speed changed to ", ParticleSystem.wind_speed)
        self._i += 1

    def verlet(self) -> None:
        for p in filter(lambda p: p.can_move, self.balls):
            temp = np.copy(p.curr_pos)
            p.curr_pos += (p.curr_pos - p.prev_pos) + \
                p.acceleration * FRAME_TIME * FRAME_TIME
            p.prev_pos = temp

    def accumulate_forces(self) -> None:
        for ball in filter(lambda b: b.can_move, self.balls):
                if ball.curr_pos[1] >= WIND_START_Y:
                    ball.acceleration = np.asarray((ParticleSystem.wind_speed, GRAVITY))
                else:
                    ball.acceleration = np.asarray((0.0, GRAVITY))

    NUM_ITERATIONS: float = 1

    def satisfy_constraints(self) -> None:
        for i in range(ParticleSystem.NUM_ITERATIONS):
            for ball in filter(lambda ball: ball.can_move, self.balls):
                # if the ball hits the ground, it is dead.
                if (ball.curr_pos[1] - Ball.radius) <= GROUND_Y:
                    print("Ball collided with the ground!")
                    ball.can_move = False
                    continue

                if ball.might_collide_with_wall():
                    p1 = np.asarray((WALL_X, GROUND_Y))
                    p2 = np.asarray((WALL_X, SCREEN_HEIGHT - 1))
                    collision, wall_p, penetration_distance = circle_line_intersection(
                        ball.curr_pos, Ball.radius, p1, p2)
                    if collision:
                        print("Ball Collided with the wall!")
                        print(collision, wall_p, penetration_distance)
                        velocity = ball.curr_pos - ball.prev_pos
                        restitution_coefficient: float = 0.95
                        # Only the x-component of the velocity is changed (since the wall is vertical)
                        velocity[0] *= -1 * restitution_coefficient
                        # get the ball out of the wall by sliding it to the right.
                        ball.curr_pos[0] += penetration_distance
                        # set the ball's velocity.
                        ball.prev_pos = ball.curr_pos - velocity
                        # can't possibly collide with anything else at the same time.
                        continue

                elif ball.might_collide_with_mountain():
                    # check if the ball collidies with a line of the mountain.
                    for p0, p1 in pairs(self.mountain_points):
                        result = collision_detection.circle_line_intersection(
                            ball.curr_pos, Ball.radius, p0, p1)
                        collision, mountain_p, penetration_dist = result
                        if not collision:
                            continue
                        print("Ball Collided with the mountain!")
                        print(mountain_p, penetration_dist)

                        restitution_coefficient: float = 0.50
                        # the mountain segment is the tangential vector to the collision.
                        tangential = p1 - p0
                        tangential /= np.linalg.norm(tangential)
                        # the normal is perpendicular to the mountain segment.
                        # TODO: we want the upward-pointing normal, does this matter ?
                        normal = np.asarray((-tangential[1], tangential[0]), float)

                        # move the ball out of the mountain.
                        ball.curr_pos += normal * penetration_dist
                        


                        velocity = ball.curr_pos - ball.prev_pos

                        v_tangent = np.dot(velocity, tangential)
                        v_normal = np.dot(velocity, normal)

                        # inelastic collision: the normal component is reversed.
                        v_normal *= -1 * restitution_coefficient
                        new_velocity = v_tangent * tangential + v_normal * normal
                        # set the ball's velocity
                        ball.prev_pos = ball.curr_pos - new_velocity
                        break
                min_constraint = (0, GROUND_Y)
                max_constraint = (SCREEN_WIDTH, SCREEN_HEIGHT)
                ball.curr_pos = np.max([ball.curr_pos, min_constraint], axis=0)
                ball.curr_pos = np.min([ball.curr_pos, max_constraint], axis=0)

            for turkey in self.turkeys:
                for constraint in turkey.stick_constraints:
                    pass

                for attached_p, constraint in p.attached_particles.items():
                    # Pseudo-code to satisfy (C2)
                    delta = p.curr_pos - attached_p.curr_pos
                    delta_dot = np.dot(delta, delta)
                    delta_length = np.sqrt(delta_dot)
                    diff = (delta_length-constraint)/delta_length
                    p.curr_pos -= delta*0.5*diff
                    attached_p.curr_pos += delta*0.5*diff

                # Pseudo-code for satisfying (C2) using sqrt approximation
                # rest_length = c.length
                # delta = c.p2.curr_pos - c.p1.curr_pos
                # delta*=rest_length*rest_length/(delta*delta+rest_length*rest_length)-0.5
                # c.p1.curr_pos -= delta
                # c.p2.curr_pos += delta

                # if c.p1.inv_mass == 0 and c.p2.inv_mass == 0:
                #     # the two particles are immovable.
                #     continue

                # # Pseudo-code to satisfy (C2) while taking mass into account.
                # p1, p2 = c.p1, c.p2
                # delta = p2.curr_pos - p1.curr_pos
                # deltalength = np.sqrt(np.dot(delta, delta))
                # diff = (deltalength - c.rest_length)
                # diff /= (deltalength * (p1.inv_mass + p2.inv_mass))
                # p1.curr_pos -= p1.inv_mass * delta * diff
                # p2.curr_pos += p2.inv_mass * delta * diff

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


def main():
    """ Main method """
    try:
        game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
        game.setup()
        arcade.run()
    finally:
        arcade.close_window()


if __name__ == "__main__":
    main()
