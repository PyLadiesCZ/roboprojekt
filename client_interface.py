"""
Client which send messages to server
"""
import asyncio
import aiohttp
import json
import pyglet

from interface_frontend import draw_interface, create_window, handle_text
from interface import get_interface_state


class Interface:
    def __init__(self):
        self.window = create_window()
        self.window.push_handlers(on_draw=self.window_draw, on_text=self.on_text)
        self.state = get_interface_state()
        self.ws = None

    def window_draw(self):
        self.window.clear()
        draw_interface(self.state, self.window)

    def on_text(self, text):
        """
        Key listener.
        Wait for user input on keyboard and react for it.
        """
        handle_text(self.state, text)
        self.send_to_server(self.state)

    def send_to_server(self, state):
        """
        Client sends selected cards to server.
        """
        msg = json.dumps(self.state.my_program)
        print(msg)
        if self.ws:
            asyncio.ensure_future(self.ws.send_str(msg))

    async def send_one(self):
        """
        Client connects to server and receives messages.
        """
        # create Session
        async with aiohttp.ClientSession() as session:
            # create Websocket
            async with session.ws_connect('http://localhost:8080/interface/') as self.ws:
                async for msg in self.ws:
                    # Cycle "for" is finished when client disconnect from server
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if msg.data.startswith("robot"):
                            robot = msg.data
                            print(robot)
                        if msg.data.startswith("cards"):
                            cards = msg.data
                            print(cards)
        self.ws = None

def tick_asyncio(dt):
    """
    Schedule an event loop.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0))


interface = Interface()

pyglet.clock.schedule_interval(tick_asyncio, 1/30)
asyncio.ensure_future(interface.send_one())

pyglet.app.run()
