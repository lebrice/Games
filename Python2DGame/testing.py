import arcade
import numpy as np

from midpoint_bisection import *
import arcade
import physics

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_Y = SCREEN_HEIGHT / 6
MOUNTAIN_WIDTH = SCREEN_WIDTH / 3
MOUNTAIN_X_MIN = SCREEN_WIDTH / 3
MOUNTAIN_X_MAX = MOUNTAIN_X_MIN + MOUNTAIN_WIDTH
MOUNTAIN_Y_MAX = SCREEN_HEIGHT / 2
MOUNTAIN_Y_MIN = GROUND_Y
MOUNTAIN_HEIGHT = MOUNTAIN_Y_MAX - MOUNTAIN_Y_MIN
WALL_X = 0

# class Ball(Particle):
#     def __init__(self, position):
#         super(position)
#         position: Tuple[float, float]
#         mass: float = 1


class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.turkeys = None
        self.mountain_points = [
            Point(MOUNTAIN_X_MIN, MOUNTAIN_Y_MIN),
            Point(int(MOUNTAIN_X_MIN + 0.50 * (MOUNTAIN_WIDTH)), MOUNTAIN_Y_MAX),
            Point(MOUNTAIN_X_MAX, MOUNTAIN_Y_MIN),
        ]
        self.wall_points = [
            Point(WALL_X, GROUND_Y),
            Point(WALL_X, SCREEN_HEIGHT - 1),
        ]
        self.particle_system: physics.ParticleSystem = None
        self.ball = None

    def setup(self):
        # Create your sprites and sprite lists here
        self.mountain_points = midpoint_bisection(self.mountain_points, max_iterations=4)
        # print([int(p.y) for p in self.mountain_points])
        self.particle_system = physics.ParticleSystem()
        self.ball = physics.Particle((SCREEN_WIDTH / 2, SCREEN_HEIGHT - 1), mass=1.0)
        self.particle_system.particles.append(self.ball)

    def on_draw(self):
        """
        Render the screen.
        """
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()
        self.draw_background()
        self.draw_mountain()
        self.draw_wall()
        self.draw_ball()
        # Call draw() on all your sprite lists below

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.particle_system.time_step()
        pass

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        pass

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

    def draw_mountain(self):
        """
        draws the mountain
        """
        arcade.draw_polygon_filled(self.mountain_points, arcade.color.BROWN_NOSE)
        # for p1, p2 in pairs(self.mountain_points):
            # arcade.draw_line(p1.x, p1.y, p2.x, p2.y, arcade.color.BLACK, 3)
            # arcade.draw_polygon_filled()

    def draw_wall(self):
        """Draws the wall on the left side of the screen."""
        arcade.draw_line(*self.wall_points[0], *self.wall_points[1], arcade.color.BLACK, 10)

    def draw_ball(self):
        center_x = self.ball.curr_pos[0]
        center_y = self.ball.curr_pos[1]
        arcade.draw_circle_filled(center_x, center_y, 5.0, arcade.color.BLACK)

def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()

