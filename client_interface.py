"""
Client which send one message to server
"""
import asyncio
import sys
import aiohttp
import json
import pyglet

from interface_frontend import draw_interface, program

window = pyglet.window.Window()

@window.event
def on_draw():
    """
    Draw the game state (board and robots).
    """
    window.clear()
    draw_interface(window)


async def send_one(msg):
    # create Session
    async with aiohttp.ClientSession() as session:
        #create Websocket
        async with session.ws_connect('http://localhost:8080/ws/') as ws:
            # send text message to server
            await ws.send_str(msg)


message = json.dumps(program)


def tick_asyncio(dt):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0))

pyglet.clock.schedule_interval(tick_asyncio, 1/30)
asyncio.ensure_future(send_one(message))

pyglet.app.run()
