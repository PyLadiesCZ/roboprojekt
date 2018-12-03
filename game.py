"""
The game module
    - coordinate everything and run the game
    - call pyglet window, various backend and frontend functions
    - choose standard or other map to be loaded
"""

import backend
import frontend
import pyglet
import sys

# load JSON map data from the backend module
if len(sys.argv) == 1:
    map_name = "maps/test_3.json"

# if other map should be loaded, use extra argument "maps/MAP_NAME.json" when calling game.py by Python
        # for example: python game.py maps/test_2.json
else:
    map_name = sys.argv[1]

# Load JSON map data from the backend module.
data = backend.get_data(map_name)

# Get starting state of the game from the backend module.
state = backend.get_start_state(data)


# Load pyglet graphic window from the frontend module.
window = frontend.init_window(frontend.WINDOW_WIDTH, frontend.WINDOW_HEIGHT)


@window.event
def on_draw():
    """
    Clears the graphic window and draw the game board and robots.
    """

    # load pyglet sprites by the frontend module
    tile_sprites = frontend.load_tiles(state, frontend.TILE_WIDTH, frontend.TILE_HEIGHT)
    robot_sprites = frontend.load_robots(state, frontend.TILE_WIDTH, frontend.TILE_HEIGHT)

    window.clear()
    frontend.draw_board(tile_sprites, robot_sprites)


def move_once(t):
    """
    Move all robots 2 tiles forward and rotate 180 degrees.
    """

    for robot in state.robots:
        robot.walk(2)
        robot.rotate("upside_down")

pyglet.clock.schedule_once(move_once, 3)

# Run the pyglet library.
pyglet.app.run()
