import asyncio
import sys


def tick_asyncio(dt):
    """
    Schedule an event loop.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0))


def set_argument_value(default):
    """
    Return the value of the first argument from command line.
    If it is empty, ergo only the file name was used,
    return the set default value.
    default: string
    """
    return default if len(sys.argv) == 1 else sys.argv[1]
