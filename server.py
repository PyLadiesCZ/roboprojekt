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

#vytvořit stav
state = get_start_state(map_name)

websockets = []

routes = web.RouteTableDef()

@routes.get("/ws/")
async def websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    websockets.append(ws)
    try:
        await ws.send_str(json.dumps(state.as_dict(map_name), indent=1))

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(msg.data) #měnit stav
                for client in websockets:
                    #poslat info o stavu
                    await client.send_str(json.dumps(state.as_dict(map_name), indent=1))

        return ws
    finally:
            websockets.remove(ws)


def get_app(argv=None):
    app = web.Application()
    app.add_routes(routes)
    return app

if __name__ == '__main__':
    app = get_app()
    web.run_app(app)
