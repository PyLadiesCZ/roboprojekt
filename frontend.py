"""
The frontend module
    - deal with graphic output
    - define a Pyglet window for drawing and create sprites from images
"""

import pyglet

# Constatnts for size of tile image in px
TILE_WIDTH = 64
TILE_HEIGHT = 64


def create_window(state):
    """
    Return a pyglet window for graphic output.

    state: State object containing game board, robots and map sizes
    """
    window = pyglet.window.Window(state.tile_count[0] * TILE_WIDTH,
                                  state.tile_count[1] * TILE_HEIGHT, resizable=True)
    return window


def load_tiles(state):
    """
    Return list of sprites of tiles.

    state: State object containing game board and robots
    """
    tile_sprites = []
    for coordinate, tiles in state._board.items():
        sprites = create_sprites(coordinate, tiles)
        tile_sprites.extend(sprites)
    return tile_sprites


def load_robots(state):
    """
    Return list of sprites of robots.

    state: State object containing game board and robots
    """
    robot_sprites = []
    # Only active robots will be drawn.
    for robot in state.get_active_robots():
        robot_sprite = create_sprites(robot.coordinates, [robot])
        robot_sprites.extend(robot_sprite)
    return robot_sprites


def create_sprites(coordinate, items):
    """
    Return list of sprites of items.

    coordinate: coordinate of tiles or robot
    items: a list of Tile or Robot objects
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


def draw_state(state, window):
    """
    Draw the images of tiles and robots into map, react to user's resizing of window by scaling the board.

    state: State object containing game board, robots and map sizes
    """
    tile_sprites = load_tiles(state)
    robot_sprites = load_robots(state)
    tile_sprites.extend(robot_sprites)

    #scaling
    pyglet.gl.glPushMatrix()

    #scaling ratio
    zoom = min(
        window.height / (state.tile_count[1] * TILE_HEIGHT),
        window.width / (state.tile_count[0] * TILE_WIDTH)
    )

    pyglet.gl.glScalef(zoom, zoom, 1)

    for tile_sprite in tile_sprites:
        tile_sprite.draw()

    pyglet.gl.glPopMatrix()
