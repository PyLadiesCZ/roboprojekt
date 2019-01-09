"""
The game module
    - coordinate everything and run the game
    - call pyglet window, various backend and frontend functions
    - choose standard or other map to be loaded
"""

from backend import get_start_state
from frontend import init_window, draw_board, TILE_WIDTH, TILE_HEIGHT
import pyglet
import sys

# load JSON map data from the backend module
if len(sys.argv) == 1:
    map_name = "maps/test_3.json"

# if other map should be loaded, use extra argument "maps/MAP_NAME.json" when calling game.py by Python
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
    Draw the game state (board and robots) and react to user's resizing of window by scaling the board.
    """
    
    # find out maximal screen size of user
    platform = pyglet.window.get_platform()
    display = platform.get_default_display()
    screen = display.get_default_screen()
    screen_width = screen.width
    screen_height = screen.height

    window.clear()
    
    #scaling
    pyglet.gl.glPushMatrix()
    
    #scaling ratio
    zoom = min(
        window.height / (state.sizes[1] * TILE_HEIGHT),
        window.width / (state.sizes[0] * TILE_WIDTH)
    )
    
    pyglet.gl.glScalef(zoom, zoom, 1)
    
    draw_board(state)
    
    pyglet.gl.glPopMatrix()
    
def move_once(t):
    """
    Move all robots 2 tiles forward and rotate 180 degrees.
    """

    for robot in state.robots:
        robot.walk(3, state)
        robot.rotate("upside_down")

pyglet.clock.schedule_once(move_once, 3)

# Run the pyglet library.
pyglet.app.run()
