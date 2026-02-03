"""
Welcome board, where player can choose his robot and name.
Client receives game state with available robots from server.
If you want to change robot's name, just type on the keyboard.
Max lenght of the name is 8 characters.
Then click on the chosen robot.
"""
import asyncio
import aiohttp
import pyglet
pyglet.options['shadow_window'] = False

import click

from backend import State
from util_network import tick_asyncio
from welcome_board_frontend import create_window, draw_board, handle_click
from client_interface import run_from_welcome_board as interface_main


class WelcomeBoard:
    def __init__(self, hostname):
        self.own_robot_name = ""
        self.window = create_window(
            self.window_draw,
            self.on_mouse_press,
            self.on_text,
            self.on_text_motion,
        )
        self.state = None
        self.available_robots = None
        self.hostname = hostname

    def window_draw(self):
        """
        Draw the window with available robots.
        """
        self.window.clear()
        draw_board(
            self.state,
            self.available_robots,
            self.window,
            self.own_robot_name,
        )

    def on_mouse_press(self, x, y, button, mod):
        """
        Board is handled by mouse press.
        """
        chosen_robot = handle_click(self.state, x, y, self.window, self.available_robots)
        if chosen_robot is not None:
            interface_main(chosen_robot, self.own_robot_name, self.hostname)
            self.window.close()

    def on_text(self, text):
        """
        Welcome board reacts on input text. Set up own robot name (max 8 char.)
        """
        if len(self.own_robot_name) < 8:
            if text != '\r':
                self.own_robot_name = self.own_robot_name + text

    def on_text_motion(self, motion):
        """
        React on backspace motion - when it is pressed, delete one letter.
        """
        if motion == pyglet.window.key.MOTION_BACKSPACE:
            self.own_robot_name = self.own_robot_name[:-1]

    async def process_message(self):
        """
        Connect to server and receive messages.
        Process information from server.
        """
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://' + self.hostname + ':8080/receiver/') as ws:
                # Loop "for" is finished when client disconnects from server
                async for message in ws:
                    message = message.json()
                    if "game_state" in message:
                        self.state = State.whole_from_dict(message)
                        if self.window is None:
                            self.window = create_window(
                                self.window_draw,
                                self.on_mouse_press,
                                self.on_text,
                                self.on_text_motion,
                            )
                    if "available_robots" in message:
                        self.available_robots = self.state.robots_from_dict({"robots": message["available_robots"]})


@click.command()
@click.option("-h", "--hostname", default="localhost",
              help="Server's hostname.")
def main(hostname):
    welcome_board = WelcomeBoard(hostname)
    pyglet.clock.schedule_interval(tick_asyncio, 1/30)
    # Schedule the "client" task
    # More about Futures - official documentation
    # https://docs.python.org/3/library/asyncio-future.html
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.ensure_future(welcome_board.process_message())
    pyglet.app.run()


if __name__ == "__main__":
    main()
