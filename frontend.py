"""
The frontend module
    - deal with graphic output
    - define a Pyglet window for drawing and create sprites from images
"""

import pyglet


def init_window():
    """
    Return a pyglet window for graphic outputself.

    data: a dict created from decoded Tiled 1.2 JSON file
    """
    from game import WINDOW_WIDTH, WINDOW_HEIGHT

    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
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
    from game import TILE_WIDTH, TILE_HEIGHT

    items_sprites = []
    for item in items:
        rotation = item.rotation
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


def draw_board(tile_sprites, robot_sprites):
    """
    Draw the images of tiles and robots into map.

    tile_sprites: a list of tiles sprites
    robot_sprites: a list of robots sprites
    """
    tile_sprites.extend(robot_sprites)
    for tile_sprite in tile_sprites:
        tile_sprite.draw()
