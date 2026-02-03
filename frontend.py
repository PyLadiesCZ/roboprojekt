"""
The frontend module
    - deal with graphic output
    - define a Pyglet window for drawing and create sprites from images
"""

import pyglet
pyglet.options['shadow_window'] = False

from pyglet.gl import Config as GLConfig
from pathlib import Path
from time import monotonic
from util_frontend import (TILE_WIDTH, TILE_HEIGHT, get_label, get_sprite, window_zoom,
                           _init_module_after_gl_context as _util_frontend_init_module_after_gl_context)
import math


loaded_tiles_images = {}  # init inside _init_module_after_gl_context
loaded_robots_images = {} # init inside _init_module_after_gl_context

_init_module_after_gl_context_called = False

def _init_module_after_gl_context():
    """ Loading of tiles and robots images
        because of the gl.gl_compat functions we need to load sprites
        after a window with correct GL context is created
    """
    global loaded_tiles_images, loaded_robots_images
    global border_sprite, winner_sprite #, game_over_sprite
    global _init_module_after_gl_context_called
    if _init_module_after_gl_context_called:
        return
    _init_module_after_gl_context_called = True

    for image_path in Path('./img/tiles/png').iterdir():
        loaded_tiles_images[image_path.stem] = pyglet.image.load(str(image_path))

    for image_path in Path('./img/robots_map/png').iterdir():
        loaded_robots_images[image_path.stem] = pyglet.image.load(str(image_path))

    # Border of available robot's picture
    border_sprite = get_sprite('./img/interface/png/border.png')
    # Winner
    winner_sprite = get_sprite('img/interface/png/game_winner.png', x=170, y=200)
    # Game over
    # game_over_sprite = get_sprite('img/interface/png/game_over.png', x=140, y=180)


def create_window(state, on_draw):
    """
    Return a pyglet window for graphic output.
    Loads global sprites in the first call after the window is created with compatible GL context.

    state: State object containing game board, robots and map sizes
    """
    gl_config = GLConfig(major_version=2, minor_version=1, forward_compatible=False)
    window = pyglet.window.Window(state.tile_count[0] * TILE_WIDTH,
                                  state.tile_count[1] * TILE_HEIGHT + 50,
                                  config=gl_config, resizable=True)
    _util_frontend_init_module_after_gl_context()
    _init_module_after_gl_context()

    window.push_handlers(on_draw=on_draw)
    return window


def load_tiles(state):
    """
    Return list of sprites of tiles.

    state: State object containing game board and robots
    """
    tile_sprites = []
    for coordinate, tiles in state._board.items():
        sprites = create_tile_sprites(coordinate, tiles)
        tile_sprites.extend(sprites)
    return tile_sprites


def load_robots(state, last_robots, animation_pos):
    """
    Return list of sprites of robots.

    state: State object containing game board and robots
    """
    robot_sprites = []
    # Only active robots will be drawn.
    for robot in state.robots:
        last_robot = last_robots.get(robot.name, robot)
        robot_sprite = create_robot_sprite(robot, last_robot, animation_pos)
        if robot_sprite != None:
            robot_sprites.append(robot_sprite)
    return robot_sprites


def create_tile_sprites(coordinate, tiles):
    """
     Return list of sprites of tiles.

    coordinate: coordinate of tiles
    tiles = list of Tile
    """
    tile_sprites = []
    for tile in tiles:
        rotation = tile.direction.value
        x, y = coordinate
        img = loaded_tiles_images[tile.name]
        img.anchor_x = img.width//2
        img.anchor_y = img.height//2
        tile_x = x*TILE_WIDTH
        tile_y = y*TILE_HEIGHT
        tile_sprite = pyglet.sprite.Sprite(img, x=img.anchor_x + tile_x,
                                                y=img.anchor_y + tile_y)
        tile_sprite.rotation = rotation
        tile_sprites.append(tile_sprite)
    return tile_sprites


def create_robot_sprite(robot, last_robot, animation_pos):
    """
    Return sprite of robot.
    """
    # The sprite is positioned at a point between "last_robot" and "robot"
    # given by the "animation_pos".
    # "animation_pos" can range between 0 (for "last_robot") through
    # 1 (for "robot"), or anything in between for that point in the animation.

    # Any of the "last_robot" or "robot" coordinates may be None. In that case,
    # we want to use the other set of coordinates.
    x1, y1 = coalesce(last_robot.coordinates, robot.coordinates, (None, None))
    x2, y2 = coalesce(robot.coordinates, last_robot.coordinates, (None, None))
    # If both were None, don't draw this robot at all.
    if x1 == None:
        return None
    x = lerp(x1, x2, animation_pos)
    y = lerp(y1, y2, animation_pos)

    # Rotation
    rot1 = last_robot.direction.value
    rot2 = robot.direction.value
    # When turning from 270 to 0 degrees, we actually want 270 -> 360
    if (rot1 - rot2) > 180:
        rot2 = rot2 + 360
    # When turning from 0 to 270 degrees, we actually want 360 -> 270
    if (rot2 - rot1) > 180:
        rot1 = rot1 + 360
    rotation = lerp(rot1, rot2, animation_pos)

    # When the robot is out of the game, set its scale to 0.
    # This gives reasonable "fall in hole" and "re-appear" animations.
    if last_robot.coordinates == None:
        scale1 = 0
    else:
        scale1 = 1
    if robot.coordinates == None:
        scale2 = 0
    else:
        scale2 = 1
    scale = lerp(scale1, scale2, animation_pos)

    # Show change in damage by animating the color:
    # - when damage is received, fade to red (255, 0, 0)
    # - when healed, fade to green (0, 255, 0)
    # - otherwise, keep normal colors (255, 255, 255)
    # Additionally, wiggle the robot by changing its rotation.
    fading_color = 255 * (1 - animation_pos)
    if robot.damages > last_robot.damages:
        color = 255, fading_color, fading_color
        rotation += math.sin(animation_pos * math.pi * 4) * 10
    elif robot.damages < last_robot.damages:
        color = fading_color, 255, fading_color
        rotation += math.sin(animation_pos * math.pi * 2) * 10
    else:
        color = 255, 255, 255
    animation_pos = monotonic() / 0.2

    # Prepare the sprite
    img = loaded_robots_images[robot.name]
    img.anchor_x = img.width//2
    img.anchor_y = img.height//2
    robot_x = x*TILE_WIDTH
    robot_y = y*TILE_HEIGHT
    robot_sprite = pyglet.sprite.Sprite(img, x=img.anchor_x + robot_x,
                                             y=img.anchor_y + robot_y)
    robot_sprite.rotation = rotation
    robot_sprite.scale = scale
    robot_sprite.color = color
    return robot_sprite


def coalesce(*args):
    """Return the first non-None argument"""
    for arg in args:
        if arg != None:
            return arg


def lerp(start, end, t):
    """Linear interpolation between "start" and "end" at time "t"

    t must be between 0 (for the start) and 1 (for the end)
    See: https://en.wikipedia.org/wiki/Linear_interpolation#Programming_language_support
    """
    return start * (1-t) + end * t


def draw_state(state, winner_time, available_robots, window, last_robots=None, animation_pos=1):
    """
    Draw the images of tiles and robots into map, react to user's resizing of window by scaling the board.

    state: State object containing game board, robots and map sizes.
    Winner_time is the time, when client received message about winner.

    If "last_robots" is given, display a frame of the animation between
    the state given in "last_robots" and the one in "state".
    The state of the animation is given by "animation_pos", which should be
    between 0 (for "last_robots", the start of the animation) and 1 (for
    "state", the end of the animation).
    The "last_robots" argument should be a dict of {robot name: robot}.
    """
    if last_robots == None:
        last_robots = {}
    tile_sprites = load_tiles(state)
    robot_sprites = load_robots(state, last_robots, animation_pos)
    tile_sprites.extend(robot_sprites)

    with window_zoom(
        window, state.tile_count[0] * TILE_WIDTH,
        state.tile_count[1] * TILE_HEIGHT + 50
    ):
        for tile_sprite in tile_sprites:
            tile_sprite.draw()

        if available_robots:
            for robot in available_robots:
                x, y = robot.coordinates
                for robot_sprite in robot_sprites:
                    border_sprite.x = robot_sprite.x*TILE_WIDTH
                    border_sprite.y = robot_sprite.y*TILE_HEIGHT
                    border_sprite.draw()

        if state.winners:
            #game_over_sprite.draw()
            winner_label = get_label(
                "WINNER",
                x=150,
                y=state.tile_count[1] * TILE_HEIGHT + 10,
                font_size=20,
                anchor_x="right",
                color=(255, 255, 255, 255),
            )
            winner_label.draw()

            for i, name in enumerate(state.winners):
                winner_name_label = get_label(
                    str(name),
                    x=300 + 165 * i,
                    y=state.tile_count[1] * TILE_HEIGHT + 10,
                    font_size=20,
                    anchor_x="right",
                    color=(255, 255, 255, 255),
                )
                winner_name_label.draw()

            # Picture of winner is drawn for 5 sec from time,
            # when client received message about winner.
            seconds = 5 - (monotonic() - winner_time)
            if (0 < seconds < 5):
                winner_sprite.draw()
                for i, name in enumerate(state.winners):
                    winner_label = get_label(
                        str(name),
                        x=(state.tile_count[0] * TILE_WIDTH) / 2 - 50,
                        y=(state.tile_count[1] * TILE_HEIGHT) / 2 - 100 - i * 50,
                        font_size=26,
                        anchor_x="center",
                        color=(255, 0, 0, 255),
                    )
                    winner_label.draw()
