#this file is still in progress
import pyglet
import backend
WIDTH = 12
HEIGHT = 12
TILE_WIDTH = 64
TILE_HEIGHT = 64


'''this function make  window for drawing'''
def init_window(data, WIDTH, HEIGHT):
    window = pyglet.window.Window(WIDTH, HEIGHT)
    return window

'''this function make a list of images'''
def load_images(data, state, TILE_WIDTH, TILE_HEIGHT):
    real_images = backend.get_real_ids(data)
    images = []
    for key in state:
        if state[key] in real_images:
            img = pyglet.image.load(real_images[state[key]])
            img.anchor_x = img.width//2
            img.anchor_y = img.height//2
            x, y = key
            tile_x = x*TILE_WIDTH
            tile_y = y*TILE_HEIGHT
            img = pyglet.sprite.Sprite(img, x=img.anchor_x+tile_x, y = img.anchor_y+tile_y)
            images.append(img)
    return images

'''this function is drawing a map'''
def draw_board(state, images):

    for tile in images:
        tile.draw()


#WIP
