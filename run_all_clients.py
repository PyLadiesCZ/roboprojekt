"""
Run clients with a single file.
Depending on number of players on the map add another interfaces.
Don´t forget to run server.py in another command line.

For devel purposes.
"""
import pyglet

import client_receiver
import client_welcome_board

client_receiver.main()
client_welcome_board.main()
client_welcome_board.main()

pyglet.app.run()
