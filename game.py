import backend
import frontend
import pyglet

TILE_WIDTH = 64
TILE_HEIGHT = 64
WINDOW_WIDTH = 12*TILE_WIDTH
WINDOW_HEIGHT = 12*TILE_HEIGHT

map_name = "./maps/test_3.json"
data = backend.get_data(map_name)

window = frontend.init_window(WINDOW_WIDTH, WINDOW_HEIGHT)

coordinates = backend.get_coordinates(data)
tilelist = backend.get_tiles(data)
state = backend.get_coordinate_dict(coordinates, tilelist)

images = frontend.load_images(data, state, TILE_WIDTH, TILE_HEIGHT)


@window.event
def on_draw():
    window.clear()
    frontend.draw_board(state, images)


pyglet.app.run()
