import pyglet
from pathlib import Path
from client_interface import main

from interface_frontend import get_sprite, get_label

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500

class WelcomeBoard:
    def __init__(self):
        self.window = pyglet.window.Window(1024, 500, resizable=True)
        self.available_robots

    def window_draw(self):
        """
        Draw the game state (board and robots).
        """
        self.window.clear()
        draw_state(self.state, self.window)

    async def get_game_state(self):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://localhost:8080/receiver/') as ws:
                # Cycle "for" is finished when client disconnects from server
                async for message in ws:
                    message = message.json()


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

    x = 50 + i * 120
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

    sorted_dict = sorted(loaded_robots_images.keys())
    for coordinate, robot in zip(picture_coordinates, sorted_dict):
        robot_sprite.image = loaded_robots_images[robot]
        x, y = coordinate
        robot_sprite.x = x
        robot_sprite.y = y
        robot_sprite.draw()

        robot_name_label = get_label(
            str(robot), x + 30, y - 20, 16, "center", (0, 0, 0, 255)
        )
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

            main()
            window.close()

window.push_handlers(
    on_draw=draw_board,
    on_mouse_press=on_mouse_press
)

pyglet.app.run()
