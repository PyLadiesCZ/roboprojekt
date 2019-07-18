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

from aiohttp import web

from backend import State


class Server:
    def __init__(self, map_name):
        self.map_name = map_name
        self.state = State.get_start_state(map_name)

        self.available_robots = list(self.state.robots)
        # Dictionary {robot_name: ws_interface}
        self.assigned_robots = {}

        # A list of connected clients
        self.ws_receivers = []
        self.ws_interfaces = []
        # Routing table for aiohttp.web
        self.routes = []

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

    async def receiver(self, request):
        async with self.ws_handler(request, self.ws_receivers) as ws:
            # This message is sent only this (just connected) client
            await ws.send_json(self.state.as_dict(map_name), dumps=json.dumps)
            # For cycle keeps the connection with client alive
            async for msg in ws:
                pass
            return ws

    async def interface(self, request):
        async with self.ws_handler(request, self.ws_interfaces) as ws:
            # This message is sent only this (just connected) client
            # Client_interface is added to dictionary (robot.name: ws)
            name = self.available_robots[0].name
            self.assigned_robots[name] = ws
            print(self.assigned_robots)

            robot = self.available_robots.pop(0)
            await ws.send_json({"robot_name": robot.name}, dumps=json.dumps)
            await ws.send_json(self.state.as_dict(map_name), dumps=json.dumps)

            dealt_cards = self.state.get_dealt_cards(robot)
            await ws.send_json(self.state.cards_as_dict(dealt_cards), dumps=json.dumps)

            # Process messages from this client
            async for msg in ws:
                message = msg.json(loads=json.loads)
                # it is still possible to choose cards
                # TODO: not only by pressing key but also with time up
                if not message["interface_data"]["confirmed"]:
                    robot.power_down = message["interface_data"]["power_down"]
                    robot.program = []
                    for card_index in message["interface_data"]["my_program"]:
                        if card_index is None:
                            robot.program.append(None)
                        else:
                            robot.program.append(dealt_cards[card_index])
                # choice of cards was blocked by the player
                else:
                    # Add the rest of the cards to used cards pack
                    for card in robot.program:
                        if card is not None:
                            try:
                                dealt_cards.remove(card)
                            except ValueError:
                                break
                    self.state.add_to_past_deck(dealt_cards)
                    print(robot.program)

                # Send messages to all connected clients
                ws_all = self.ws_receivers + self.ws_interfaces
                for client in ws_all:
                    # send info about state
                    await client.send_json(self.state.as_dict(map_name), dumps=json.dumps)
            return ws

if len(sys.argv) == 1:
    map_name = "maps/test_2.json"
else:
    map_name = sys.argv[1]

server = Server(map_name)

# aiohttp.web application
def get_app(argv=None):
    app = web.Application()
    app.add_routes([web.get("/receiver/", server.receiver),
                   web.get("/interface/", server.interface), ],
                   )
    return app


if __name__ == '__main__':
    app = get_app()
    web.run_app(app)
