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

from config import *
from physics import ParticleSystem, Ball
from utils import pairs

# from turkey import Turkey
# Set the working directory (where we expect to find files) to the same
# directory this .py file is in. You can leave this out of your own
# code, but it is needed to easily run the examples using "python -m"
# as mentioned at the top of this program.
file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)
IMAGE_DIR = os.path.join(os.path.curdir, "images")

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
        if key == arcade.key.P:
            image = arcade.get_image()
            path = f"screenshot_{MyGame.i}.png"
            image.save(path)
            print("Saved a screenshot at path: ", path)

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
        # TODO: can't have the turkey moving while it is also in the air!

        for t in self.turkeys:
            # BUG: The jumping doesn't work!
            # randomly jump about every 5 seconds
            if MyGame.i %  random.randint(3 * FRAME_RATE, 6 * FRAME_RATE) == 0:
                t.jump()
            
            if MyGame.i % (3 * FRAME_RATE) == 0:
                t.pacing_speed = random_speed()
            # TODO: only move the turkeys like this if they are below the wind ?
            if t.center_x - t.radius <= WALL_X:
                # we want to force the turkey to move right
                t.pacing_speed = abs(t.pacing_speed)
            elif t.center_x + t.radius >= MOUNTAIN_X_MIN:
                # we want to force the turkey to move left
                t.pacing_speed *= - abs(t.pacing_speed)

            #FIXME: Moving the turkey like this seems like a bad idea! (but its the only thing that works right now)
            t.move(t.pacing_speed, 0.0)
            # Much better would be to have the pacing be some kind of acceleration or velocity:
            # t.velocity[0] = t.pacing_speed
            # print(t.velocity[0])

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
