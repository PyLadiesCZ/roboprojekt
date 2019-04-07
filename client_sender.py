"""
Client which send one message to server
"""
import asyncio
import sys
import aiohttp


async def send_one(msg):
    # create Session
    async with aiohttp.ClientSession() as session:
        #create Websocket
        async with session.ws_connect('http://localhost:8080/ws/') as ws:
            # send text message to server
            await ws.send_str(msg)

# Message can be written in command line
try:
    message = sys.argv[1]
except IndexError:
    # Example, will e edited
    message = "My card is..."

asyncio.run(send_one(message))
