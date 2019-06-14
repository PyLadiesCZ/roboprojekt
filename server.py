"""
The server will run and play the game.
More info about creating server and client -
https://aiohttp.readthedocs.io/en/stable/index.html

Run server.py in command line, in new command line run client_receiver.py,
it will receive messages from server. You can send one message to server,
which will be displayed - in another command line open client_sender.py
with argument(message) - "python client_sender.py Hello".
"""
import sys
import json

import aiohttp
from aiohttp import web

from backend import get_start_state, get_robot_names
from interface import create_card_pack


if len(sys.argv) == 1:
    map_name = "maps/test_3.json"
else:
    map_name = sys.argv[1]

# Create state, will be edited
state = get_start_state(map_name)

card_pack = create_card_pack()
card_pack = str(card_pack)
robots = get_robot_names()

# A list of connected clients
ws_receivers = []
ws_interfaces = []
# Routing table for aiohttp.web
routes = web.RouteTableDef()


@routes.get("/receiver/")
async def receiver(request):
    # Prepare WebSocket
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    # WebSocket is added to a list
    ws_receivers.append(ws)
    try:
        # This message is sent only this (just connected) client
        # await ws.send_str(robots[0])
        await ws.send_json(state.as_dict(map_name), dumps=json.dumps)
        # await ws.send_str(card_pack)

        # Process messages from this client
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(msg.data)

                # Send messages to all connected clients
                for client in ws_receivers:
                    # send info about state
                    await client.send_str(json.dumps(state.as_dict(map_name)))
        return ws
    finally:
            # after disconnection client is removed from list
            ws_receivers.remove(ws)


@routes.get("/interface/")
async def interface(request):
    # Prepare WebSocket
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    # WebSocket is added to a list
    ws_interfaces.append(ws)
    try:
        # This message is sent only this (just connected) client
        await ws.send_str(f"robot, {robots[0]}")
        # await ws.send_json(state.as_dict(map_name), dumps=json.dumps)
        await ws.send_str(f"cards, {card_pack}")

        # Process messages from this client
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(msg.data)

                # Send messages to all connected clients
                for client in ws_interfaces:
                    # send info about state
                    await client.send_str(json.dumps(state.as_dict(map_name)))

        return ws
    finally:
            # after disconnection client is removed from list
            ws_interfaces.remove(ws)


# aiohttp.web application
def get_app(argv=None):
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    app = get_app()
    web.run_app(app)
