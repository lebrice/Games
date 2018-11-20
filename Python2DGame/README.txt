COMP 521 Assignment #2 - Fabrice Normandin - McGill ID 260636800

This simple game is built using the Python Arcade library.

General Notes:
- The scheme for the turkey constrains and geometry is shown in the "turkey.pdf" file.
- Turkeys aren't totally finished. They are implemented using verlets, and they pace around the left side, but they don't jump or interact with the ball yet.
- All physics-related code can be found inside `physics.py`, config values in `config.py`, midpoint bisection in `midpoint_bisection.py`, etc.

Controls:
- UP ARROW to move the cannon up
- DOWN ARROW to move the cannon down. (Note: each keypress changes the angle by 5 degrees).
- SPACE_BAR to shoot a ball
- P to take a screenshot.

Requirements:
- Python 3.6+
- `pip install ./requirements.txt`
    - NOTE: for Windows, the Shapely package (used in collision detection) might fail to install. In that case, the appropriate shapely wheel has to be downloaded from this site:
    https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely (look for the wheel corresponding to your Python version) 
    - Wheels for python 3.6 and 3.7 were included in this directory (to install them, run "pip install ./Shapely-1.6.4.(...).whl")

To run the game, then simply execute `game.py` from the command line.
