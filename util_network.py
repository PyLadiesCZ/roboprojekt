import argparse
import asyncio


def parse_args():
    """
    Add command line optional arguments:
     `-s`, `--server-hostname`: set your server's IP address.
     `-m`, `--map`: map which will be played.
    Return arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server-hostname", help="set custom server IP")
    parser.add_argument("-m", "--map", help="set custom game map")
    args = parser.parse_args()
    return args


def set_server_ip():
    """
    Return server IP: either custom, or 'localhost' if not filled in.
    """
    args = parse_args()
    return args.connection if args.connection else "localhost"


def set_map_name():
    """
    Return map name to play: either custom, or 'maps/test_winner.json'
    if not filled in.
    """
    args = parse_args()
    return args.map if args.map else "maps/test_winner.json"


def tick_asyncio(dt):
    """
    Schedule an event loop.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0))
