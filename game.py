import backend
import frontend
import pyglet

BOARD_HEIGHT = 12 # tiles count, previously: data['layers'][0]['height']
BOARD_WIDTH = 12 # tiles count, previously: data['layers'][0]['width']
TILE_WIDTH = 64 # tile size, value in px
TILE_HEIGHT = 64 # tile size, value in px
WINDOW_WIDTH = BOARD_HEIGHT*TILE_WIDTH # value in px
WINDOW_HEIGHT = BOARD_WIDTH*TILE_HEIGHT # value in px

map_name = "./maps/test_3.json"
data = backend.get_data(map_name)

window = frontend.init_window(WINDOW_WIDTH, WINDOW_HEIGHT)

coordinates = backend.get_coordinates(BOARD_HEIGHT, BOARD_WIDTH)
tilelist = backend.get_tiles(data)
state = backend.get_coordinate_dict(coordinates, tilelist)

images = frontend.load_images(data, state, TILE_WIDTH, TILE_HEIGHT)


@window.event
def on_draw():
    window.clear()
    frontend.draw_board(state, images)


pyglet.app.run()
