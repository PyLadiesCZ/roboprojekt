"""
The frontend module
    - deal with graphic output
    - define a Pyglet window for drawing and create sprites from images
"""

import pyglet

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


def load_images(state, TILE_WIDTH, TILE_HEIGHT):
    """
    return list of images

    input needed - loaded data fron JSON, dictionary state, size of tiles
    """

    images = []
    for layer in state.board:
        img = sprite(state.board[layer], TILE_WIDTH, TILE_HEIGHT)
        # print(state.board[layer])
        images.extend(img)
    return images


def load_robots(state, TILE_WIDTH, TILE_HEIGHT):
    """
    return sprites of robots

    input needed - dictionary state, size of tiles
    """
    robots = sprite(state.robots, TILE_WIDTH, TILE_HEIGHT)
    return robots


def sprite(img_dict, TILE_WIDTH, TILE_HEIGHT):
    """
    return list of sprites of items

    input needed - dictionary img_dict, size of tiles
    """
    list = []
    for coordinate, value in img_dict.items():
        rotation = value.rotation
        path = value.path
        if path != 0:
            x, y = coordinate
            img = pyglet.image.load(path)
            img.anchor_x = img.width//2
            img.anchor_y = img.height//2
            tile_x = x*TILE_WIDTH
            tile_y = y*TILE_HEIGHT
            img = pyglet.sprite.Sprite(img, x=img.anchor_x+tile_x, y=img.anchor_y+tile_y)
            img.rotation = rotation
            list.append(img)
    return list


def draw_board(images, robots):
    """
    draw the images of tiles into map
    """
    images.extend(robots)
    for tile in images:
        tile.draw()
