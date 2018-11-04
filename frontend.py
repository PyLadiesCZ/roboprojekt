#this file is still in progress
import pyglet
import backend

map_name = "./test_1.json"
data = backend.get_data(map_name)

def get_windowsize(data):#in backend?
    map_field_height = data['layers'][0]['height']
    map_field_width = data['layers'][0]['width']
    tile_height = data['tileheight']
    tile_width = data['tilewidth']
    width = tile_width*map_field_width
    height = tile_height*map_field_height
    return width,height, tile_width, tile_height

size = get_windowsize(data)
width = size[0]
height = size[1]
tile_width = size[2]
tile_height= size[3]
coordinates = backend.get_coordinates(data)
tilelist = backend.get_tiles(data)
state = backend.get_coordinate_dict(coordinates,tilelist)
real_images = backend.get_real_ids(data)
#lines 5 to 25 should be in backend/game.py?

def draw_board():
    images = []
    for key in state:
        if state[key] in real_images:
            img = pyglet.image.load(real_images[state[key]])
            img.anchor_x = img.width//2
            img.anchor_y = img.height//2
            x, y = key
            tile_x = x*tile_width
            tile_y = y*tile_height
            img = pyglet.sprite.Sprite(img, x=img.anchor_x+tile_x, y = img.anchor_y+tile_y)
            images.append(img)
    return images

window = pyglet.window.Window(width, height)
tiles = draw_board()

#rest should be in game.py???  line 46-54
@window.event
def on_draw():
    window.clear()

    for tile in tiles:
        tile.draw()

pyglet.app.run()

#WIP
