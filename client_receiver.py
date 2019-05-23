"""
Client receive messages from server and print them
"""

import asyncio
import sys
import aiohttp
import json
import pyglet

from backend import State
from frontend import draw_state

window = pyglet.window.Window()

state = None

@window.event
def on_draw():
    """
    Draw the game state (board and robots).
    """
    window.clear()
    if state:
        draw_state(state, window)


async def client():
    global state
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/ws/') as ws:
            # Waiting for message from server and print them
            async for msg in ws:
                # Cycle "for" is finished when client disconnect from server
                if msg.type == aiohttp.WSMsgType.TEXT:
                    message = msg.data
                    state_dict = json.loads(message)
                    state = State.from_dict(state_dict)
                    print(state_dict)


def tick_asyncio(dt):
    """
    Schedule an event loop.
    More about event loop - https://docs.python.org/3/library/asyncio-eventloop.html
    """
    loop = asyncio.get_event_loop()
    # Run the loop until the "asyncio.sleep" task is complete
    loop.run_until_complete(asyncio.sleep(0))

pyglet.clock.schedule_interval(tick_asyncio, 1/30)

# Schedule the "client" task
# More about Futures - official documentation https://docs.python.org/3/library/asyncio-future.html
asyncio.ensure_future(client())
pyglet.app.run()
