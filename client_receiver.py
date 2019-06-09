"""
Client receive messages from server and print them
"""
import asyncio
import aiohttp
import json
import pyglet

from backend import State
from frontend import draw_state, create_window

state = None
window = None


def on_draw():
    """
    Draw the game state (board and robots).
    """
    window.clear()
    if state:
        draw_state(state, window)


async def client():
    global state
    global window
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/receiver/') as ws:
            # Waiting for message from server and print them
            async for msg in ws:
                # Cycle "for" is finished when client disconnects from server
                try:
                    message = msg.json(loads=json.loads)
                    state = State.from_dict(message)
                    window = create_window(state)
                    window.push_handlers(on_draw=on_draw)
                    print("state is", state)
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


pyglet.clock.schedule_interval(tick_asyncio, 1/30)

# Schedule the "client" task
# More about Futures - official documentation https://docs.python.org/3/library/asyncio-future.html
asyncio.ensure_future(client())


pyglet.app.run()
