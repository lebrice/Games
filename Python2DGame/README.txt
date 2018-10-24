COMP 521 Assignment #2 - Fabrice Normandin - McGill ID 260636800

This simple game is built using the Python Arcade library, which can be installed via Pip.

General Notes:
- Turkeys aren't exactly completed. They are made of a verlet system, but the collision hasn't been done yet.
- The scheme for the turkey constrains and geometry is shown in the "turkey.pdf" file.




Requirements:
- Python 3.6+
- `pip install ./requirements.txt`
    - NOTE: for Windows, the Shapely package will fail to install. In that case, the appropriate shapely wheel has to be downloaded from this site:
    https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely (look for the wheel corresponding to your Python version) (a Wheel for python 3.7 was included in this directory)


To run the game, then simply execute `game.py` from the command line.
