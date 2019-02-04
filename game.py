"""
The game module
    - coordinate everything and run the game
    - call pyglet window, various backend and frontend functions
    - choose standard or other map to be loaded
"""

from backend import get_start_state, apply_tile_effects
from frontend import init_window, draw_board
import pyglet
import sys


# load JSON map data from the backend module
if len(sys.argv) == 1:
    map_name = "maps/test_effects.json"

# if other map should be loaded, use extra argument "maps/MAP_NAME.json"
# when calling game.py by Python
# for example: python game.py maps/test_2.json
else:
    map_name = sys.argv[1]

# Get starting state of the game from the backend module.
state = get_start_state(map_name)

# Load pyglet graphic window from the frontend module.
window = init_window(state)


@window.event
def on_draw():
    """
    Draw the game state (board and robots).
    """

    window.clear()
    draw_board(state, window)


def move_once(t):
    """
    Move all robots according to mock cards on hand and perform tile effects.
    """

    for robot in state.robots:
        # robot.apply_card_effect(state)
        robot.walk(3, state)
        # print(robot)

    apply_tile_effects(state)
    print("After tile effects:")
    for robot in state.robots:
        print(robot)


pyglet.clock.schedule_once(move_once, 3)

# Run the pyglet library.
pyglet.app.run()
