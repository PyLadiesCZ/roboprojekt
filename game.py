"""
The game module
    - coordinate everything and run the game
    - call pyglet window, various backend and frontend functions
    - choose standard or other map to be loaded
"""
import pyglet
import sys

from backend import get_start_state, play_the_game
from frontend import create_window, draw_state


# load JSON map data from the backend module
if len(sys.argv) == 1:
    map_name = "maps/test_effects.json"

# if other map should be loaded, use extra argument "maps/MAP_NAME.json"
# when calling game.py by Python
# for example: python game.py maps/test_2.json
else:
    map_name = sys.argv[1]

# Get start state of the game from the backend module.
state = get_start_state(map_name)

# Load pyglet graphic window from the frontend module.
window = create_window(state)


@window.event
def on_draw():
    """
    Draw the game state (board and robots).
    """

    window.clear()
    draw_state(state, window)


def move_once(t):
    """
    Move all robots according to mock cards on hand and perform tile effects.
    """

    play_the_game(state)
    print("After tile effects:")
    for robot in state.robots:
        print(robot)


pyglet.clock.schedule_once(move_once, 3)

# Run the pyglet library.
pyglet.app.run()
