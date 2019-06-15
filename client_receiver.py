"""
Client receive messages from server and print them
"""
import asyncio
import aiohttp
import json
import pyglet

from backend import State
from frontend import draw_state, create_window


class Receiver:
    def __init__(self):
        self.window = None
        self.state = None


    def window_draw(self):
        """
        Draw the game state (board and robots).
        """
        self.window.clear()
        draw_state(self.state, self.window)


    async def client(self):
        window = None
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://localhost:8080/receiver/') as ws:
                # Waiting for message from server and print them
                async for msg in ws:
                    # Cycle "for" is finished when client disconnects from server
                    try:
                        message = msg.json(loads=json.loads)
                        self.state = State.from_dict(message)
                        if self.window is None:
                            self.window = create_window(self.state)
                            self.window.push_handlers(on_draw=self.window_draw)
                        print("state is", self.state)
                    except json.decoder.JSONDecodeError:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            message = msg.data
                            print("cards are", message)


def tick_asyncio(dt):
    """
    Schedule an event loop.
    More about event loop - https://docs.python.org/3/library/asyncio-eventloop.html
    """
    loop = asyncio.get_event_loop()
    # Run the loop until the "asyncio.sleep" task is complete
    loop.run_until_complete(asyncio.sleep(0))

receiver = Receiver()

pyglet.clock.schedule_interval(tick_asyncio, 1/30)

# Schedule the "client" task
# More about Futures - official documentation https://docs.python.org/3/library/asyncio-future.html
asyncio.ensure_future(receiver.client())


pyglet.app.run()
