# this file is still in progress
import pyglet
import backend

'''this function make  window for drawing'''
def init_window(WINDOW_WIDTH, WINDOW_HEIGHT):
    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    return window

'''this function make a list of images'''
def load_images(data, state, TILE_WIDTH, TILE_HEIGHT):
    real_images = backend.get_real_ids(data)
    images = []
    for layer in state:
        for key, value in state[layer].items():
            coordinate, rotation = value
            if coordinate in real_images:
                img = pyglet.image.load(real_images[coordinate])
                img.anchor_x = img.width//2
                img.anchor_y = img.height//2
                x, y = key
                tile_x = x*TILE_WIDTH
                tile_y = y*TILE_HEIGHT
                img = pyglet.sprite.Sprite(img, x=img.anchor_x+tile_x, y=img.anchor_y+tile_y)
                img.rotation = rotation
                images.append(img)
    return images

'''this function is drawing a map'''
def draw_board(state, images):

    for tile in images:
        tile.draw()


# WIP
