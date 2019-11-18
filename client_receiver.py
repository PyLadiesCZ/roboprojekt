"""
Client receives game state from server and draws it.
"""
import asyncio
import aiohttp
import pyglet
import click
from time import monotonic
from util_network import tick_asyncio

from backend import State
from frontend import draw_state, create_window


class Receiver:
    def __init__(self, hostname, game_name):
        self.window = None
        self.state = None
        self.available_robots = None
        self.winner_time = None
        self.hostname = hostname
        self.game_name = game_name

    def window_draw(self):
        """
        Draw the game state (board and robots).
        """
        self.window.clear()
        draw_state(self.state, self.winner_time, self.available_robots, self.window)

    async def get_game_state(self):
        """
        Connect to server and receive messages.
        Process information from server.
        """
        print("tu")
        async with aiohttp.ClientSession() as session:
            # print('http://' + self.hostname + ':8080/receiver/')
            async with session.ws_connect('http://' + self.hostname + ':8080/receiver/' + self.game_name) as ws:
                # Cycle "for" is finished when client disconnects from server
                async for message in ws:
                    message = message.json()
                    if "game_state" in message:
                        self.state = State.whole_from_dict(message)
                        if self.window is None:
                            self.window = create_window(self.state, self.window_draw)
                    if "robots" in message:
                        self.state.robots = self.state.robots_from_dict(message)
                    if "winner" in message:
                        self.state.winners = message["winner"]
                        self.winner_time = monotonic()
                    if "available_robots" in message:
                        self.available_robots = self.state.robots_from_dict({"robots": message["available_robots"]})


@click.command()
@click.option("-h", "--hostname", default="localhost",
              help="Server's hostname.")
@click.argument("game_name")
def main(hostname, game_name):
    receiver = Receiver(hostname, game_name)
    pyglet.clock.schedule_interval(tick_asyncio, 1/30)
    # Schedule the "client" task
    # More about Futures - official documentation
    # https://docs.python.org/3/library/asyncio-future.html
    asyncio.ensure_future(receiver.get_game_state())
    pyglet.app.run()


if __name__ == "__main__":
    main()
