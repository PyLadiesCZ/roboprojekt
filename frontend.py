"""
The frontend module
    - deal with graphic output
    - define a Pyglet window for drawing and create sprites from images
"""

import pyglet
from pathlib import Path
from time import monotonic
from util_frontend import TILE_WIDTH, TILE_HEIGHT, get_label, get_sprite, window_zoom


# Loading of tiles and robots images
loaded_tiles_images = {}
for image_path in Path('./img/tiles/png').iterdir():
    loaded_tiles_images[image_path.stem] = pyglet.image.load(image_path)

loaded_robots_images = {}
for image_path in Path('./img/robots_map/png').iterdir():
    loaded_robots_images[image_path.stem] = pyglet.image.load(image_path)

# Border of available robot's picture
border_sprite = get_sprite('./img/interface/png/border.png')
# Winner
winner_sprite = get_sprite('img/interface/png/game_winner.png', x=170, y=200)
# Game over
# game_over_sprite = get_sprite('img/interface/png/game_over.png', x=140, y=180)


def create_window(state, on_draw):
    """
    Return a pyglet window for graphic output.

    state: State object containing game board, robots and map sizes
    """
    window = pyglet.window.Window(state.tile_count[0] * TILE_WIDTH,
                                  state.tile_count[1] * TILE_HEIGHT + 50, resizable=True)
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


def load_robots(state):
    """
    Return list of sprites of robots.

    state: State object containing game board and robots
    """
    robot_sprites = []
    # Only active robots will be drawn.
    for robot in state.get_active_robots():
        robot_sprite = create_robot_sprite(robot)
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


def create_robot_sprite(robot):
    """
    Return sprite of robot.
    """
    rotation = robot.direction.value
    x, y = robot.coordinates
    img = loaded_robots_images[robot.name]
    img.anchor_x = img.width//2
    img.anchor_y = img.height//2
    robot_x = x*TILE_WIDTH
    robot_y = y*TILE_HEIGHT
    robot_sprite = pyglet.sprite.Sprite(img, x=img.anchor_x + robot_x,
                                             y=img.anchor_y + robot_y)
    robot_sprite.rotation = rotation
    return robot_sprite


def draw_state(state, winner_time, available_robots, window):
    """
    Draw the images of tiles and robots into map, react to user's resizing of window by scaling the board.

    state: State object containing game board, robots and map sizes.
    Winner_time is the time, when client received message about winner.
    """
    tile_sprites = load_tiles(state)
    robot_sprites = load_robots(state)
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
                    border_sprite.x = x*TILE_WIDTH
                    border_sprite.y = y*TILE_HEIGHT
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
                        y=(state.tile_count[1] * TILE_HEIGHT) / 2 - i * 50,
                        font_size=26,
                        anchor_x="center",
                        color=(255, 0, 0, 255),
                    )
                    winner_label.draw()
