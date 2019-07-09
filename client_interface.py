"""
Client which send messages to server
"""
import asyncio
import aiohttp
import json
import pyglet

from interface_frontend import draw_interface, create_window, handle_text
from interface import InterfaceState
from backend import State, Robot


class Interface:
    def __init__(self):
        self.window = create_window()
        self.window.push_handlers(
            on_draw=self.window_draw,
            on_text=self.on_text, )
        self.state = InterfaceState()
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
        self.send_to_server(self.state.as_dict())

    def send_to_server(self, message):
        """
        Client sends messages to server.
        """
        print(message)
        if self.ws:
            asyncio.ensure_future(self.ws.send_json(message, dumps=json.dumps))

    async def get_messages(self):
        """
        Client connects to server and receives messages.
        """
        # create Session
        async with aiohttp.ClientSession() as session:
            # create Websocket
            async with session.ws_connect('http://localhost:8080/interface/') as self.ws:
                async for msg in self.ws:
                    # Cycle "for" is finished when client disconnect from server
                    message = msg.json(loads=json.loads)
                    if "game_state" in message:
                        self.set_game_state(message)
                    elif "robot_data" in message:
                        self.set_robot_data(message)
                    elif "cards" in message:
                        self.set_dealt_cards(message)
                    else:
                        print(message)
        self.ws = None

    def set_game_state(self, message):
        self.game_state = State.from_dict(message)
        self.state.players = self.game_state.robots
        for robot in self.state.players:
            if robot.name == self.state.robot.name:
                index = self.state.players.index(robot)
                del self.state.players[index]
        # print(self.state.players)

    def set_robot_data(self, message):
        robot = Robot.from_dict(message)
        self.state.robot = robot
        # print(robot)

    def set_dealt_cards(self, message):
        self.state.dealt_cards = self.game_state.cards_from_dict(message)
        # print(self.state.dealt_cards)


def tick_asyncio(dt):
    """
    Schedule an event loop.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0))


interface = Interface()

pyglet.clock.schedule_interval(tick_asyncio, 1/30)
asyncio.ensure_future(interface.get_messages())

pyglet.app.run()
