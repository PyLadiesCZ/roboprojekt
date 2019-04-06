#tento klient posílá (interface)
import asyncio
import sys

import aiohttp


async def send_one(msg):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/ws/') as ws:
            await ws.send_str(msg)

try:
    message = sys.argv[1]
except IndexError:
    message = "Můj tah je..."

asyncio.run(send_one(message))
