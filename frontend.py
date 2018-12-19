"""
The frontend module
    - deal with graphic output
    - define a Pyglet window for drawing and create sprites from images
"""

import pyglet

# Constatnts for size of tile image in px
TILE_WIDTH = 64
TILE_HEIGHT = 64

def init_window(state):
    """
    Return a pyglet window for graphic outputself.

    data: a dict created from decoded Tiled 1.2 JSON file
    """
    window = pyglet.window.Window(state.sizes[0] * TILE_WIDTH,
                                  state.sizes[1] * TILE_HEIGHT, resizable=True)
    return window

def load_tiles(state):
    """
    Return list of sprites of tiles.

    state: State object containing game board and robots
    data: a dict created from decoded Tiled 1.2 JSON file
    """
    tile_sprites = []
    for coordinate, tiles in state.board.items():
        sprites = sprite(coordinate, tiles)
        tile_sprites.extend(sprites)
    return tile_sprites


def load_robots(state):
    """
    Return list of sprites of robots.

    state: State object containing game board and robots
    data: a dict created from decoded Tiled 1.2 JSON file
    """
    robot_sprites = []
    for robot in state.robots:
        robot_sprite = sprite(robot.coordinates, [robot])
        robot_sprites.extend(robot_sprite)
    return robot_sprites


def sprite(coordinate, items):
    """
    Return list of sprites of items.

    coordinate: coordinate of tiles or robot
    items: a list of Tile or Robot objects
    data: a dict created from decoded Tiled 1.2 JSON file
    """
    items_sprites = []
    for item in items:
        rotation = item.direction.value
        path = item.path
        x, y = coordinate
        img = pyglet.image.load(path)
        img.anchor_x = img.width//2
        img.anchor_y = img.height//2
        item_x = x*TILE_WIDTH
        item_y = y*TILE_HEIGHT
        img_sprite = pyglet.sprite.Sprite(img, x=img.anchor_x + item_x,
                                               y=img.anchor_y + item_y)
        img_sprite.rotation = rotation
        items_sprites.append(img_sprite)
    return items_sprites


def draw_board(state):
    """
    Draw the images of tiles and robots into map.

    state: State object containing game board and robots
    """
    window = pyglet.window.Window(state.sizes[0] * TILE_WIDTH,
                                  state.sizes[1] * TILE_HEIGHT, resizable=True)
    tile_sprites = load_tiles(state)
    robot_sprites = load_robots(state)
    tile_sprites.extend(robot_sprites)

    pyglet.gl.glPushMatrix()
    zoom = min(
        window.height / 200,
        window.width / 200
    )
    pyglet.gl.glScalef(zoom, zoom, 1)

    for tile_sprite in tile_sprites:
        tile_sprite.draw()

    pyglet.gl.glPopMatrix()
