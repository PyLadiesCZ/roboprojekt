"""
Welcome board where player can choose his robot.
Client receives game state with available robots from server.
"""
import asyncio
import aiohttp
import pyglet

from backend import State
from util_network import tick_asyncio
from welcome_board_frontend import create_window, draw_board, handle_click


class WelcomeBoard:
    def __init__(self):
        self.window = create_window(self.window_draw, self.on_mouse_press)
        self.state = None
        self.available_robots = None

    def window_draw(self):
        """
        Draw the window with available robots.
        """
        self.window.clear()
        draw_board(self.state, self.available_robots, self.window)

    def on_mouse_press(self, x, y, button, mod):
        """
        Board is handled by mouse press.
        """
        handle_click(self.state, x, y, self.window, self.available_robots)

    async def process_message(self):
        """
        Connect to server and receive messages.
        Process information from server.
        """
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://localhost:8080/receiver/') as ws:
                # Loop "for" is finished when client disconnects from server
                async for message in ws:
                    message = message.json()
                    if "game_state" in message:
                        self.state = State.whole_from_dict(message)
                        if self.window is None:
                            self.window = create_window(self.window_draw, self.on_mouse_press)
                    if "available_robots" in message:
                        self.available_robots = self.state.robots_from_dict({"robots": message["available_robots"]})


def main():
    welcome_board = WelcomeBoard()
    pyglet.clock.schedule_interval(tick_asyncio, 1/30)

    # Schedule the "client" task
    # More about Futures - official documentation
    # https://docs.python.org/3/library/asyncio-future.html
    asyncio.ensure_future(welcome_board.process_message())


if __name__ == "__main__":
    main()
    pyglet.app.run()
