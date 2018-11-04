#this file is still in progress
import pyglet
import backend

'''making of window based on function
def get_windowsize(data):
    map_field_height = data['layers'][0]['height']
    map_field_width = data['layers'][0]['width']
    tile_height = data['tileheight']
    tile_width = data['tilewidth']
    width = tile_width*map_field_width
    height = tile_height*map_field_height
    return width,height, tile_width, tile_height'''

def init_window(data):
    size = backend.get_windowsize(data)
    width = size[0]
    height = size[1]
    tile_width = size[2]
    tile_height= size[3]
    window = pyglet.window.Window(width, height)
    return window

#list of images
def load_images(data, state):
    real_images = backend.get_real_ids(data)
    size = backend.get_windowsize(data)
    tile_width = size[2]
    tile_height= size[3]
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

#drawing function
def draw_board(state, images):

    for tile in images:
        tile.draw()


#WIP
