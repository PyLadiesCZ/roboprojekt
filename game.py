"""
The game module
    - coordinate everything and run the game
    - call pyglet window, various backend and frontend functions
"""

import backend
import frontend
import pyglet
import sys


# Get map name from command line.
# Enable user to select game map, when launched from command line.
# To run for exmaple game on 'test_2' map enter: python game.py maps/test_2.json
# When game map isn't specified, default map is set to "maps/test_3.json".
if len(sys.argv) == 1:
    map_name = "maps/test_3.json"
else:
    map_name = sys.argv[1]

# Load JSON map data from the backend module.
data = backend.get_data(map_name)

# Get starting state of the game from the backend module.
state = backend.get_start_state(data)

# Load pyglet graphic window from the frontend module.
window = frontend.init_window(data)

# Load pyglet sprites by the frontend module.
tile_sprites = frontend.load_tiles(state, data)
robot_sprites = frontend.load_robots(state, data)


@window.event
def on_draw():
    """
    Clears the graphic window and draw the game board.
    """
    window.clear()
    frontend.draw_board(tile_sprites, robot_sprites)


# Run the pyglet library.
pyglet.app.run()
