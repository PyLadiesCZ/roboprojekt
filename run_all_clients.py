"""
Run all clients for map - maps/test_game.json.
Don´t forget to run server.py in another command line.
"""
import pyglet

import client_receiver
import client_interface

client_receiver.main()
client_interface.main()
client_interface.main()

pyglet.app.run()
