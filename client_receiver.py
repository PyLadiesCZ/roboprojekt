"""
Client receives game state from server and draws it.
"""
import asyncio
import aiohttp
import pyglet
pyglet.options['shadow_window'] = False

import click
from time import monotonic
from util_network import tick_asyncio

from backend import State
from frontend import draw_state, create_window

# How long one state from the log should be displayed (in seconds)
LOG_FRAME_TIME = 0.2


class Receiver:
    def __init__(self, hostname):
        self.window = None
        self.state = None
        self.available_robots = None
        self.winner_time = 0
        self.hostname = hostname

        # Log of states to display in the future
        self.log_to_play = []

        # Starting point of the current animation
        self.last_robots = None

        # Time at which the current animation started
        self.animation_start = 0

    def window_draw(self):
        """
        Draw the game state (board and robots).
        """
        self.window.clear()
        animation_pos = (monotonic() - self.animation_start) / LOG_FRAME_TIME
        if animation_pos < 0:
            animation_pos = 0
        if animation_pos > 1:
            animation_pos = 1
        draw_state(
            self.state, self.winner_time, self.available_robots, self.window,
            last_robots=self.last_robots, animation_pos=animation_pos,
        )

    def reset_last_robots(self):
        """Set the starting point of the animation to the current state.
        """
        self.last_robots = {robot.name: robot for robot in self.state.robots}

    async def tick_log(self):
        """
        Set the game state for the first element from the recorded game log
        and delete it, meaning effectively play the step.
        After the given delay (in seconds), repeat.
        """
        while True:
            if self.state:
                self.reset_last_robots()
            if self.log_to_play:
                self.animation_start = monotonic()
                new_state = self.log_to_play.pop(0)
                if new_state == None:
                    if self.winner_time == 0:
                        self.winner_time = monotonic()
                else:
                    self.state.robots = self.state.robots_from_dict(new_state)
            await asyncio.sleep(LOG_FRAME_TIME)

    async def get_game_state(self):
        """
        Connect to server and receive messages.
        Process information from server.
        """
        task = asyncio.create_task(self.tick_log())
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://' + self.hostname + ':8080/receiver/') as ws:
                # for loop is finished when client disconnects from server
                async for message in ws:
                    message = message.json()
                    if "game_state" in message:
                        self.state = State.whole_from_dict(message)
                        self.reset_last_robots()
                        if self.window is None:
                            self.window = create_window(self.state, self.window_draw)
                    if "available_robots" in message:
                        self.available_robots = self.state.robots_from_dict({"robots": message["available_robots"]})
                    if 'log' in message:
                        self.log_to_play.extend(message['log'])
                    if "winner" in message:
                        self.state.winners = message["winner"]
                        self.log_to_play.append(None)

        task.cancel()


@click.command()
@click.option("-h", "--hostname", default="localhost",
              help="Server's hostname.")
def main(hostname):
    receiver = Receiver(hostname)
    pyglet.clock.schedule_interval(tick_asyncio, 1/30)
    # Schedule the "client" task
    # More about Futures - official documentation
    # https://docs.python.org/3/library/asyncio-future.html
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.ensure_future(receiver.get_game_state())
    pyglet.app.run()


if __name__ == "__main__":
    main()
