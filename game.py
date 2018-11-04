import backend
import frontend
import pyglet

map_name = "./test_1.json"
data = backend.get_data(map_name)

window = frontend.init_window(data)

coordinates = backend.get_coordinates(data)
tilelist = backend.get_tiles(data)
state = backend.get_coordinate_dict(coordinates,tilelist)

images = frontend.load_images(data, state)

@window.event
def on_draw():
    window.clear()
    frontend.draw_board(state, images)

pyglet.app.run()
