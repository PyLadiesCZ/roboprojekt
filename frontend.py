"""
The frontend module
    - deal with graphic output
    - define a Pyglet window for drawing and create sprites from images
"""

import pyglet
import backend

# define the board and size of tiles:
TILE_WIDTH = 64
TILE_HEIGHT = 64
WINDOW_WIDTH = 12*TILE_WIDTH
WINDOW_HEIGHT = 12*TILE_HEIGHT

def init_window(WINDOW_WIDTH, WINDOW_HEIGHT):
    """
    create a pyglet window for graphic output
    """
    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    return window


def load_sprites(data, state, TILE_WIDTH, TILE_HEIGHT):
    """
    return a list of Pyglet sprites with backend's load data from JSON

    input needed - loaded data fron JSON, dictionary state, size of tiles
    """
    real_images = backend.get_real_ids(data)
    sprites = []

    #fill the empty list of sprites
    for layer in state:
        # state is distioary created in backends function get_coordiante_dict
        for key, value in state[layer].items():
            coordinate = value.id
            rotation = value.rotation
            # load sprites on xy and their rotation
            if coordinate in real_images:
                img = pyglet.image.load(real_images[coordinate])
                img.anchor_x = img.width//2
                img.anchor_y = img.height//2
                x, y = key
                tile_x = x*TILE_WIDTH
                tile_y = y*TILE_HEIGHT
                img = pyglet.sprite.Sprite(img, x=img.anchor_x+tile_x, y=img.anchor_y+tile_y)
                img.rotation = rotation
                sprites.append(img)
    return sprites


def draw_board(state, sprites):
    for tile in sprites:
        tile.draw()
