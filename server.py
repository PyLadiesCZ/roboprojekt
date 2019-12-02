"""
The server will run and play the game.
More info about creating server and client -
https://aiohttp.readthedocs.io/en/stable/index.html

Run server.py in command line, in new command line run client_receiver.py,
it will display the playing area. If you want to play, run also
client_welcome_board.py in another command line.
"""
import asyncio
import click
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
    def __init__(self, map_name, players):
        # Attributes related to game logic
        self.map_name = map_name
        self.state = State.get_start_state(map_name, players)
        self.available_robots = list(self.state.robots)
        # Dictionary {robot_name: ws_interface}
        self.assigned_robots = {}

        # Attributes related to network connections
        # List of connected clients
        self.ws_receivers = []

        self.last_sent_log_position = 0

    async def ws_handler(self, request):
        """
        Set up and return the prepared websocket.
        """
        # Prepare WebSocket
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        return ws

    def available_robots_as_dict(self):
        """
        Return dictionary with available robots.
        """
        return {"available_robots": [robot.as_dict() for robot in self.available_robots]}

    async def talk_to_receiver(self, request):
        """
        Communicate with websockets connected through `/receiver/` route.

        Send them game state.
        Maintain connection to the client until they disconnect.
        """
        ws = await self.ws_handler(request)
        self.ws_receivers.append(ws)
        try:
            # This message is sent only this (just connected) client
            await ws.send_json(self.state.whole_as_dict(self.map_name))
            await ws.send_json(self.available_robots_as_dict())
            # For cycle keeps the connection with client alive
            async for message in ws:
                pass
            return ws
        finally:
            self.ws_receivers.remove(ws)

    async def talk_to_interface(self, request):
        """
        Communicate with websockets connected through `/interface/` route.

        Send them their robot name, game state and cards to choose.
        React to the messages from interface: update game state accordingly.
        Maintain connection to the client until they disconnect.
        """
        ws = await self.ws_handler(request)
        # Get first data for connected client: robot and cards
        # and assign it to client
        robot = self.assign_robot_to_client(request.match_info.get("robot_name"), ws)
        await self.send_message(self.available_robots_as_dict())

        try:
            # Prepare message to send: robot name, game state and cards
            welcome_message = {
                "robot_name": robot.name,
                **self.state.whole_as_dict(self.map_name),
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
            return ws

        finally:
            # Deleted robot from assigned and return him to available robots
            # Set the respective robot as off (power down) and confirm their
            # card selection.
            del self.assigned_robots[robot.name]
            self.available_robots.append(robot)
            await self.send_message(self.available_robots_as_dict())
            for robot_in_game in self.state.robots:
                if robot_in_game in self.available_robots:
                    robot_in_game.freeze()

    def assign_robot_to_client(self, robot_name, ws):
        """
        Assign the first available robots to the client.
        Store the pair in a dictionary of assigned robots.
        Return the assigned robot.
        """
        # Client_interface is added to dictionary (robot.name: ws)
        if robot_name is not None:
            for robot in self.available_robots:
                if robot_name == robot.name:
                    self.available_robots.remove(robot)
                    break
            else:
                # The "else" clause executes after the loop completes normally-
                # - the loop did not encounter a break statement.
                raise web.HTTPNotFound()
        else:
            robot = self.available_robots.pop(0)

        self.assigned_robots[robot.name] = ws
        # Whenever robot is assigned to the client, unset his selection.
        robot.selection_confirmed = False
        return robot

    async def process_message(self, message, robot):
        """
        Process the data sent by interface: own robot name, chosen cards,
        confirmation of selected cards, power down state, played game round.
        """
        if robot.selection_confirmed:
            return
        message = message.json()
        if "interface_data" in message:
            robot_game_round = message["interface_data"]["game_round"]
            if robot_game_round != self.state.game_round:
                return
            # Set robot's attributes according to data in message
            # Choice of cards was blocked by the player
            if message["interface_data"]["confirmed"]:
                await self.actions_after_robot_confirmed_selection(robot)
            else:
                # While selection is not confirmed, it is still possible to choose cards
                robot.power_down = message["interface_data"]["power_down"]
                # Set robot's selection with chosen card´s index
                robot.card_indexes = message["interface_data"]["program"]

        # Set own robot name as displayed name on Interface
        if "own_robot_name" in message:
            own_robot_name = message["own_robot_name"]
            if own_robot_name != "":
                robot.displayed_name = message["own_robot_name"]

        await self.send_message(self.state.robots_as_dict())

    async def actions_after_robot_confirmed_selection(self, robot):
        """
        When the player confirmed his selection, robot.selection_confirmed
        is set up on True and according confirmed_count the Timer is
        started or game round is played.
        """
        robot.selection_confirmed = True
        confirmed_count = self.state.count_confirmed_selections()
        # If last robot doesnt selected his cards, the timer starts.
        if confirmed_count == len(self.state.robots) - 1:
            await self.send_message("timer_start")
            asyncio.create_task(self.timer(self.state.game_round))
        if confirmed_count == len(self.state.robots):
            await self.play_game_round()

    async def play_game_round(self):
        """
        Run the cards' and tiles' effects.
        Send the log of the round to clients, winners (if applicable),
        round end, current robots' state and the new cards for players.
        """
        self.state.play_round()
        await self.send_message({'log': self.state.log[self.last_sent_log_position:]})
        self.last_sent_log_position = len(self.state.log)
        if self.state.winners:
            await self.send_message({"winner": self.state.winners})
        await self.send_message("round_over")
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
        Send new dealt cards to assigned robots.
        """
        for robot in self.state.robots:
            if robot in self.available_robots:
                robot.freeze()
            else:
                ws = self.assigned_robots[robot.name]
                await ws.send_json(self.state.cards_and_game_round_as_dict(
                    robot.dealt_cards, robot.select_blocked_cards_from_program(),
                    )
                )

    async def send_message(self, message):
        """
        Send message to all  clients.
        """
        ws_all = list(self.ws_receivers)
        ws_all.extend(self.assigned_robots.values())
        for client in ws_all:
            await client.send_json(message)


# aiohttp.web application
def get_app(server):
    app = web.Application()
    app.add_routes([
        web.get("/receiver/", server.talk_to_receiver),
        web.get("/interface/", server.talk_to_interface),
        web.get("/interface/{robot_name}", server.talk_to_interface)
    ])
    return app


@click.command()
@click.option("-m", "--map-name", default="maps/belt_map.json",
              help="Name of the played map.")
@click.option("-p", "--players", help="Number of players", type=int)
def main(map_name, players):
    server = Server(map_name, players)
    app = get_app(server)
    web.run_app(app)


if __name__ == '__main__':
    main()
