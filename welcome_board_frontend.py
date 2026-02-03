import pyglet
from pyglet.gl import Config as GLConfig
from util_frontend import get_sprite, get_label, window_zoom
from util_frontend import (loaded_robots_images, player_sprite_proxy,
                           _init_module_after_gl_context as _util_frontend_init_module_after_gl_context)


WINDOW_WIDTH = 1030
WINDOW_HEIGHT = 578

picture_coordinates = []
for i in range(8):
    x = 50 + i * 120
    y = 120
    picture_coordinates.append((x, y))

_init_module_after_gl_context_called = False

def _init_module_after_gl_context():
    """ loads sprites into global variables after a GL context is created. """
    global background_sprite, border_sprite, robot_background_sprite
    global not_available_label
    global _init_module_after_gl_context_called
    _init_module_after_gl_context_called = True

    # Background
    background_sprite = get_sprite('img/interface/png/board.png', x=0, y=0)
    # Border of available robot's picture
    border_sprite = get_sprite('img/interface/png/border.png')
    robot_background_sprite = get_sprite('img/interface/png/robot_bcg.png')

    not_available_label = get_label(
        "No more available robots.",
        x=500, y=50,
        font_size=20, anchor_x="center",
        color=(255, 0, 0, 255),
    )


def create_window(on_draw, on_mouse_press, on_text, on_text_motion):
    """
    Return a pyglet window for graphic output.
    """
    gl_config = GLConfig(major_version=2, minor_version=1, forward_compatible=False)
    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT,
                                  config=gl_config, resizable=True)

    _init_module_after_gl_context()
    _util_frontend_init_module_after_gl_context()

    window.push_handlers(
        on_draw=on_draw,
        on_mouse_press=on_mouse_press,
        on_text=on_text,
        on_text_motion=on_text_motion,
    )
    return window


def draw_board(state, available_robots, window, own_robot_name):
    """
    Draw the welcome board for choosing robot,
    react to user's resizing of window by scaling the board.
    """
    with window_zoom(window, WINDOW_WIDTH, WINDOW_HEIGHT):
        background_sprite.draw()

        if state is not None and available_robots is not None:
            for coordinate, robot in zip(picture_coordinates, state.robots):
                x, y = coordinate
                if robot.name in loaded_robots_images.keys():
                    robot_background_sprite.x = x
                    robot_background_sprite.y = y
                    robot_background_sprite.draw()
                    player_sprite_proxy.image = loaded_robots_images[robot.name]
                    player_sprite_proxy.x = x
                    player_sprite_proxy.y = y
                    player_sprite_proxy.draw()
                    robot_name_label = get_label(
                        str(robot.displayed_name), player_sprite_proxy.x + 30, player_sprite_proxy.y - 26,
                        16, "center", (0, 0, 0, 255),
                    )
                    robot_name_label.draw()

                for available_robot in available_robots:
                    if available_robot.name == robot.name:
                        border_sprite.x = player_sprite_proxy.x
                        border_sprite.y = player_sprite_proxy.y
                        border_sprite.draw()

            if not available_robots:
                not_available_label.draw()

            own_name_label = get_label(
                own_robot_name,
                x=445,
                y=327,
                font_size=20,
                anchor_x="left",
                color=(0, 0, 0, 255),
            )
            own_name_label.draw()


def handle_click(state, x, y, window, available_robots):
    """
    Board react on mouse press. Return robot_name when is clicked on robot.
    """
    zoom = min(
        window.height / WINDOW_HEIGHT,
        window.width / WINDOW_WIDTH
    )
    x, y = (x / zoom, y / zoom)

    for i, coordinate in enumerate(picture_coordinates):
        coord_x, coord_y = coordinate
        if (
            coord_x < x < coord_x + player_sprite_proxy.width and
            coord_y < y < coord_y + player_sprite_proxy.height
        ):
            robot_name = sorted(loaded_robots_images.keys())[i]
            for available_robot in available_robots:
                if robot_name == available_robot.name:
                    return robot_name
