"""
The server will run and play the game.
More info about creating server and client -
https://aiohttp.readthedocs.io/en/stable/index.html

Run server.py in command line, in new command line run client_receiver.py,
it will display the playing area. If you want to play, run also
client_interface.py in another command line.
"""
import sys
import contextlib
import asyncio

from aiohttp import web

from backend import State


class Server:
    """
    Rule the game and network connection logic.

    To properly initialize, give desired map name as an argument.
    Create game state, get all available robots to assign.

    Maintain connection with receivers (showing the robots on board).
    Send them game state so that they move on board.
    Maintain connection with interfaces (one robot's control console).
    Send them robots, cards and game state so that they control their robot.

    Handle diconnection nicely - remove those clients from the list.
    """
    def __init__(self, map_name):
        # Attributes related to game logic
        self.map_name = map_name
        self.state = State.get_start_state(map_name)
        self.available_robots = list(self.state.robots)
        # Dictionary {robot_name: ws_interface}
        self.assigned_robots = {}

        # Attributes related to network connections
        # List of connected clients
        self.ws_receivers = []
        self.ws_interfaces = []

    @contextlib.asynccontextmanager
    async def ws_handler(self, request, ws_list):
        """
        Context manager for server.

        Set up the websocket and add connected client to the respective list,
        depending on its role (interface or receiver).
        Yield the prepared websocket.
        When connection is disrupted, remove the client from the list.
        """
        # Prepare WebSocket
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        # WebSocket is added to a list
        ws_list.append(ws)
        try:
            yield ws
        finally:
            # after disconnection client is removed from list
            ws_list.remove(ws)

    async def talk_to_receiver(self, request):
        """
        Communicate with websockets connected through `/receiver/` route.

        Send them game state.
        Maintain connection to the client until they disconnect.
        """
        async with self.ws_handler(request, self.ws_receivers) as ws:
            # This message is sent only this (just connected) client
            await ws.send_json(self.state.whole_as_dict(map_name))
            # For cycle keeps the connection with client alive
            async for message in ws:
                pass
            return ws

    async def talk_to_interface(self, request):
        """
        Communicate with websockets connected through `/interface/` route.

        Send them their robot name, game state and cards to choose.
        React to the messages from interface: update game state accordingly.
        Maintain connection to the client until they disconnect.
        """
        async with self.ws_handler(request, self.ws_interfaces) as ws:
            # Get first data for connected client: robot and cards
            # and assign it to client
            robot = self.assign_robot_to_client(ws)
            # Prepare message to send: robot name, game state and cards
            welcome_message = {
                "robot_name": robot.name,
                **self.state.whole_as_dict(map_name),
                **self.state.cards_and_game_round_as_dict(
                    robot.dealt_cards,
                    robot.select_blocked_cards_from_program(),
                    ),
                }
            # Send the message to the connected client
            await ws.send_json(welcome_message)

            # React to the sent state of this client and send new state to all
            async for message in ws:
                await self.process_message(message, robot)
                await self.send_message(self.state.robots_as_dict())

            return ws

    def assign_robot_to_client(self, ws):
        """
        Assign the first available robots to the client.
        Store the pair in a dictionary of assigned robots.
        Return the assigned robot.
        """
        # Client_interface is added to dictionary (robot.name: ws)
        name = self.available_robots[0].name
        self.assigned_robots[name] = ws
        robot = self.available_robots.pop(0)
        return robot

    async def process_message(self, message, robot):
        """
        Process the data sent by interface: chosen cards,
        confirmation of selected cards, power down state, played game round.
        """
        if robot.selection_confirmed:
            return
        message = message.json()
        robot_game_round = message["interface_data"]["my_game_round"]
        if robot_game_round == self.state.game_round:
            # Set robot's attributes according to data in message
            # While selection is not confirmed, it is still possible to choose cards
            if not message["interface_data"]["confirmed"]:
                # TODO: this part only sets the POWER DOWN attribute,
                # it doesn't affect anything else.
                robot.power_down = message["interface_data"]["power_down"]
                # Set robot's selection with chosen card´s index
                robot.card_indexes = message["interface_data"]["my_program"]

            # choice of cards was blocked by the player
            else:
                robot.selection_confirmed = True
                selection_confirmed_number = self.state.selection_confirmed_number()

                if selection_confirmed_number == len(self.state.robots):
                    await self.play_game_round()
                # If last robot doesnt selected his cards, the timer starts.
                if selection_confirmed_number == len(self.state.robots) - 1:
                    await self.send_message("timer_start")
                    asyncio.create_task(self.timer(self.state.game_round))

    async def play_game_round(self):
        """
        Contain methods play_round, send_message(robots_as_dict),
        send_new_dealt_card.
        """
        self.state.play_round()
        await self.send_message("round_over")
        if self.state.winners:
            await self.send_message({"winner": self.state.winners})
        await self.send_message(self.state.robots_as_dict())
        await self.send_new_dealt_cards()


    async def timer(self, game_round):
        """
        Run timer for 30s.
        After timer server check if game round matches,
        then assigns random cards to his program.
        It continues to apply effects.
        """
        await asyncio.sleep(30)
        if game_round == self.state.game_round:
            await self.play_game_round()

    async def send_new_dealt_cards(self):
        """
        Send new dealt cards to robots.
        """
        for robot in self.state.robots:
            ws = self.assigned_robots[robot.name]
            await ws.send_json(self.state.cards_and_game_round_as_dict(
                robot.dealt_cards, robot.select_blocked_cards_from_program()))

    async def send_message(self, message):
        """
        Send message to all  clients.
        """
        ws_all = self.ws_receivers + self.ws_interfaces
        for client in ws_all:
            await client.send_json(message)


# aiohttp.web application
def get_app(argv=None):
    app = web.Application()
    app.add_routes([web.get("/receiver/", server.talk_to_receiver),
                   web.get("/interface/", server.talk_to_interface), ],
                   )
    return app


if __name__ == '__main__':
    if len(sys.argv) == 1:
        map_name = "maps/test_winner.json"
    else:
        map_name = sys.argv[1]

    server = Server(map_name)
    app = get_app()
    web.run_app(app)
