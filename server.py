"""
The server will run and play the game.
More info about creating server and client - https://aiohttp.readthedocs.io/en/stable/index.html

Run server.py in command line, open new command line and run client_receiver.py, it will receive
messages from server. You can send one message to server, which will be displayed - in another
command line open client_sender.py with argument(message) - "python client_sender.py Hello".
"""
import sys
import asyncio

import aiohttp
from aiohttp import web
import json
from backend import get_start_state, State

if len(sys.argv) == 1:
    map_name = "maps/test_3.json"
else:
    map_name = sys.argv[1]

# Create state, will be edited
state = get_start_state(map_name)

# A list of connected clients
websockets = []
# Routing table for aiohttp.web
routes = web.RouteTableDef()

@routes.get("/ws/")
async def websocket(request):
    # Prepare WebSocket
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    # WebSocket is add to a list
    websockets.append(ws)
    try:
        # This message is sent only this (just connected) client
        await ws.send_str(json.dumps(state.as_dict(map_name)))

        #Process messages from this cliend
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(msg.data)

                # Send messages to all connected clients
                for client in websockets:
                    # send info about state
                    await client.send_str(json.dumps(state.as_dict(map_name)))

        return ws
    finally:
            # after disconnection is client remove from list
            websockets.remove(ws)

# aiohttp.web application
def get_app(argv=None):
    app = web.Application()
    app.add_routes(routes)
    return app

if __name__ == '__main__':
    app = get_app()
    web.run_app(app)
