# klient co přijímá zprávy (obecenstvo)

import asyncio
import sys

import aiohttp


URL = 'http://localhost:8080/ws/'

async def client():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/ws/') as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(msg.data)

asyncio.run(client())
