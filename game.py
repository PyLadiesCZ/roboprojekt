"""
The game module
    - coordinate everything and run the game
    - call pyglet window, various backend and frontend functions
"""

import backend
import frontend
import pyglet

# load JSON map data from the backend module
# currently the actual map is a constant, in future probably asks the player to choose
map_name = "./maps/test_3.json"
data = backend.get_data(map_name)

# load pyglet graphic window from the frontend module
window = frontend.init_window(frontend.WINDOW_WIDTH, frontend.WINDOW_HEIGHT)

# call functions from the backend module to draw the game board
coordinates = backend.get_coordinates(data)
tilelist = backend.get_tiles(data)
state = backend.get_coordinate_dict(coordinates, tilelist)

# load pyglet sprites by the frontend module
sprites = frontend.load_sprites(data, state, frontend.TILE_WIDTH, frontend.TILE_HEIGHT)


@window.event
def on_draw():
    """
    this function clears the graphic window
    and finally draws the board game
    """
    window.clear()
    frontend.draw_board(state, sprites)

# run the pyglet library
pyglet.app.run()
