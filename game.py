"""
The module game is part of RoboProject by Pyladies Brno.

Key library is pyglet Python library  https://bitbucket.org/pyglet/pyglet/wiki/Home
This module imports the backend and frontend modules.

The game module
    - imports pyglet library, backend and frontend modules
    - provides arguments for map size
    - loads specific JSON map with 12x12 tiles with the size 64x64 px
    - calls pyglet window
    - calls various backend and frontend functions
    - draws the game map and runs pyglet
"""

import backend
import frontend
import pyglet

# definition of game board tiles and their size:
TILE_WIDTH = 64
TILE_HEIGHT = 64
WINDOW_WIDTH = 12*TILE_WIDTH
WINDOW_HEIGHT = 12*TILE_HEIGHT

# loading JSON map data from the backend module
map_name = "./maps/test_3.json"
data = backend.get_data(map_name)

# loading pyglet graphic window from the frontend module
window = frontend.init_window(WINDOW_WIDTH, WINDOW_HEIGHT)

# calling functions from the backend module to draw the game board
coordinates = backend.get_coordinates(data)
tilelist = backend.get_tiles(data)
state = backend.get_coordinate_dict(coordinates, tilelist)

# calling functions from the backend module to draw robots on startin squares
starting_coordinates = backend.get_starting_coordinates(state)
robot_paths = backend.get_robot_paths()

# loading pyglet sprites by the frontend module
images = frontend.load_images(data, state, TILE_WIDTH, TILE_HEIGHT)
robots = frontend.load_robots(starting_coordinates, robot_paths, TILE_WIDTH, TILE_HEIGHT)





@window.event
def on_draw():
    """
    this function clears the graphic window
    and finally draws the board game
    """
    window.clear()
    frontend.draw_board(state, images, robots)

# this runs the pyglet library
pyglet.app.run()
