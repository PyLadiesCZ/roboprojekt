import pyglet
import subprocess
from pathlib import Path

from interface_frontend import get_sprite, get_label

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500


# Background
background_sprite = get_sprite('img/interface/png/board.png', x=10, y=0)
# Loading of robots images
loaded_robots_images = {}
for image_path in Path('./img/robots/png').iterdir():
    loaded_robots_images[image_path.stem] = pyglet.image.load(image_path)

def get_sprite(img_path, x=0, y=0):
    img = pyglet.image.load(img_path)
    return pyglet.sprite.Sprite(img, x, y)


robot_sprite = get_sprite('img/robots/png/bender.png')

picture_coordinates = []
for i in range(8):
    x = 100 + i * 100
    y = 200
    picture_coordinates.append((x, y))

window = pyglet.window.Window(1024, 500, resizable=True)


def draw_board():
    """
    Draw the images of tiles and robots into map, react to user's resizing of window by scaling the board.

    state: State object containing game board, robots and map sizes
    """
    pyglet.gl.glPushMatrix()
    window.clear()
    zoom = min(
        window.height / WINDOW_HEIGHT,
        window.width / WINDOW_WIDTH
    )
    pyglet.gl.glScalef(zoom, zoom, 1)

    background_sprite.draw()

    for i, robot in enumerate(loaded_robots_images.keys()):
        robot_sprite.image = loaded_robots_images[robot]
        robot_sprite.x = 50 + 120 * i
        robot_sprite.y = 200
        robot_sprite.draw()

        robot_name_label = get_label(str(robot), 80 + 120 * i, 180, 16, "center", (0, 0, 0, 255))
        robot_name_label.draw()
    pyglet.gl.glPopMatrix()


def on_mouse_press(x, y, tlacitko, mod):
    zoom = min(
        window.height / WINDOW_HEIGHT,
        window.width / WINDOW_WIDTH
    )
    x, y = (x / zoom, y / zoom)

    for coordinate in picture_coordinates:
        coord_x, coord_y = coordinate
        if (
            coord_x < x < coord_x + robot_sprite.width and
            coord_y < y < coord_y + robot_sprite.height
        ):
            print("OK")
            #subprocess.run(["python", "client_interface.py"], check=True)



window.push_handlers(
    on_draw=draw_board,
    on_mouse_press=on_mouse_press
)

pyglet.app.run()
