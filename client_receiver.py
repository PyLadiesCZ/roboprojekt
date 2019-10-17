"""
Client receives game state from server and draws it.
"""
import asyncio
import aiohttp
import pyglet
from time import monotonic
from util_network import set_argument_value, tick_asyncio

from backend import State
from frontend import draw_state, create_window


class Receiver:
    def __init__(self, server_ip):
        self.window = None
        self.state = None
        self.winner_time = None
        self.server_ip = server_ip

    def window_draw(self):
        """
        Draw the game state (board and robots).
        """
        self.window.clear()
        draw_state(self.state, self.winner_time, self.window)

    async def get_game_state(self):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://' + self.server_ip + ':8080/receiver/') as ws:
                # Cycle "for" is finished when client disconnects from server
                async for message in ws:
                    message = message.json()
                    if "game_state" in message:
                        self.state = State.whole_from_dict(message)
                        if self.window is None:
                            self.window = create_window(self.state)
                            self.window.push_handlers(on_draw=self.window_draw)
                    if "robots" in message:
                        self.state.robots = self.state.robots_from_dict(message)
                    if "winner" in message:
                        self.state.winners = message["winner"]
                        self.winner_time = monotonic()


def main():
    server_ip = set_argument_value("localhost")
    receiver = Receiver(server_ip)
    pyglet.clock.schedule_interval(tick_asyncio, 1/30)

    # Schedule the "client" task
    # More about Futures - official documentation
    # https://docs.python.org/3/library/asyncio-future.html
    asyncio.ensure_future(receiver.get_game_state())


if __name__ == "__main__":
    main()
    pyglet.app.run()
