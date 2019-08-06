"""
Game interface.
Client which receives data about its robot, cards and state of the game from
server. It sends messages with its state to server.
"""
import asyncio
import aiohttp
import pyglet

from interface_frontend import draw_interface, create_window, handle_text
from interface import InterfaceState
from backend import State


class Interface:
    def __init__(self):
        # Game attributes
        self.window = create_window()
        self.window.push_handlers(
            on_draw=self.window_draw,
            on_text=self.on_text, )
        self.state = InterfaceState()
        self.game_state = None

        # Connection attribute
        self.ws = None

    def window_draw(self):
        """
        Draw the window containing game interface with its current state.
        """
        self.window.clear()
        draw_interface(self.state, self.window)

    def on_text(self, text):
        """
        Key listener.
        Wait for user input on keyboard and react for it.
        With every key press send interface state to server.
        """
        handle_text(self.state, text)
        self.send_to_server(self.state.as_dict())

    def send_to_server(self, message):
        """
        Send messages to server.
        """
        # print(message)
        if self.ws:
            asyncio.ensure_future(self.ws.send_json(message))

    async def get_messages(self):
        """
        Connect to server and receive messages.
        Process information from server: game state, robot and cards.
        """
        # create Session
        async with aiohttp.ClientSession() as session:
            # create Websocket
            async with session.ws_connect('http://localhost:8080/interface/') as self.ws:
                # Cycle "for" is finished when client disconnects from server
                async for message in self.ws:
                    message = message.json()
                    if "robot_name" in message:
                        robot_name = message["robot_name"]
                    if "game_state" in message:
                        self.set_game_state(message, robot_name)
                    if "robots" in message:
                        self.set_robots(message, robot_name)
                    if "cards" in message:
                        self.set_dealt_cards(message)
                        self.state.timer = False
                    if "winner" in message:
                        self.set_winner(message)
                    if "timer_start" in message:
                        self.state.timer = True
                    if "timer_end" in message:
                        self.set_timer_off(message)
        self.ws = None

    def set_game_state(self, message, robot_name):
        """
        Set game attributes using data from server message:
        - create game state, call set_robots.
        """
        self.game_state = State.whole_from_dict(message)
        self.set_robots(message["game_state"], robot_name)

    def set_robots(self, message, robot_name):
        """
        Set robots, players and self robot using data from sent message.
        """
        self.game_state.robots = self.game_state.robots_from_dict(message)
        self.state.players = self.game_state.robots
        for robot in self.state.players:
            if robot.name == robot_name:
                self.state.robot = robot
                index = self.state.players.index(robot)
                del self.state.players[index]

    def set_dealt_cards(self, message):
        """
        Set dealt cards and game round using data from server message.
        """
        self.state.selection_confirmed = False
        self.state.dealt_cards = self.game_state.cards_from_dict(message)
        self.state.return_cards()
        # Set the game round for this client - it is changed only
        # by message from server
        self.state.my_game_round = message["current_game_round"]

    def set_winner(self, message):
        """
        Set winner from received message.
        """
        winner = message["winner"]
        self.state.winner = winner

    def set_timer_off(self, message):
        """
        Set timer for client. It check game round for timer off.
        """
        state_game_round = message["timer_end"]["game_round"]
        if state_game_round == self.state.my_game_round:
            self.state.timer = False


def tick_asyncio(dt):
    """
    Schedule an event loop.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0))


def main():
    interface = Interface()

    pyglet.clock.schedule_interval(tick_asyncio, 1/30)
    asyncio.ensure_future(interface.get_messages())


if __name__ == "__main__":
    main()
    pyglet.app.run()
