import pyglet
from pathlib import Path

from util_frontend import get_sprite, get_label, window_zoom


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500

# Background
background_sprite = get_sprite('img/interface/png/board.png', x=10, y=0)
# Loading of robots images
loaded_robots_images = {}
for image_path in Path('./img/robots/png').iterdir():
    loaded_robots_images[image_path.stem] = pyglet.image.load(image_path)
# Border of available robot's picture
border_sprite = get_sprite('./img/interface/png/border.png')
# Robot sprite
robot_sprite = get_sprite('img/robots/png/bender.png')

picture_coordinates = []
for i in range(8):
    x = 50 + i * 120
    y = 200
    picture_coordinates.append((x, y))

not_available_label = get_label(
    "No more available robots.",
    x=500, y=50,
    font_size=20, anchor_x="center",
    color=(255, 0, 0, 255),
)


def create_window(on_draw, on_mouse_press):
    """
    Return a pyglet window for graphic output.
    """
    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, resizable=True)
    window.push_handlers(on_draw=on_draw, on_mouse_press=on_mouse_press)
    return window


def draw_board(state, available_robots, window):
    """
    Draw the welcome board for choosing robot,
    react to user's resizing of window by scaling the board.
    """
    with window_zoom(window, WINDOW_WIDTH, WINDOW_HEIGHT):
        background_sprite.draw()

        if state is not None:
            for coordinate, robot in zip(picture_coordinates, state.robots):
                x, y = coordinate
                if robot.name in loaded_robots_images.keys():
                    robot_sprite.image = loaded_robots_images[robot.name]
                    robot_sprite.x = x
                    robot_sprite.y = y
                    robot_sprite.draw()

                    robot_name_label = get_label(
                        str(robot.displayed_name), robot_sprite.x + 30, robot_sprite.y - 20,
                        16, "center", (0, 0, 0, 255),
                    )
                    robot_name_label.draw()

                for available_robot in available_robots:
                    if available_robot.name == robot.name:
                        border_sprite.x = robot_sprite.x
                        border_sprite.y = robot_sprite.y
                        border_sprite.draw()

            if not available_robots:
                not_available_label.draw()


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
            coord_x < x < coord_x + robot_sprite.width and
            coord_y < y < coord_y + robot_sprite.height
        ):
            robot_name = sorted(loaded_robots_images.keys())[i]
            for available_robot in available_robots:
                if robot_name == available_robot.name:
                    return robot_name
