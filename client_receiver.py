"""
Client receive messages from server and print them
"""

import asyncio
import sys
import aiohttp
import json

from backend import state_from_dict


async def client():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/ws/') as ws:
            # Waiting for message from server and print them
            async for msg in ws:
                # Cycle "for" is finished when client disconnect from server
                if msg.type == aiohttp.WSMsgType.TEXT:
                    message = msg.data
                    state_dict = json.loads(message)
                    state = state_from_dict(state_dict)
                    print(state_dict)

asyncio.run(client())
