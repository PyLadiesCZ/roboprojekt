"""
The game module
    - coordinate everything and run the game
    - call pyglet window, various backend and frontend functions
"""

import backend
import frontend
import pyglet
import sys

# load JSON map data from the backend module

if len(sys.argv) == 1:
    map_name = "maps/test_3.json"
else:
    map_name = sys.argv[1]
    
data = backend.get_data(map_name)

# load pyglet graphic window from the frontend module
window = frontend.init_window(frontend.WINDOW_WIDTH, frontend.WINDOW_HEIGHT)


state = backend.get_start_state(data)

# load pyglet sprites by the frontend module
images = frontend.load_images(state, frontend.TILE_WIDTH, frontend.TILE_HEIGHT)
robots = frontend.load_robots(state, frontend.TILE_WIDTH, frontend.TILE_HEIGHT)


@window.event
def on_draw():
    """
    this function clears the graphic window
    and finally draws the board game
    """
    window.clear()
    frontend.draw_board(images, robots)


# this runs the pyglet library
pyglet.app.run()
