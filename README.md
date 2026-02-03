# RoboProject

This is a video game based on the board game [RoboRally](https://en.wikipedia.org/wiki/RoboRally).

It includes a network server and graphical desktop clients.

### The Project
*Advanced PyLadies CZ Project*

This project was created for PyLadies who successfully passed beginner Python courses and wanted to continue with Python via a "real" assignment. Its aim was to show participants the process of software development from the very basics, and enable them to try it on their own. It was focused on team cooperation, using Python for real tasks, working with Git and GitHub, showing best practices and trying various useful tools.

You can read about the progress on our [blog](https://roboprojekt.pyladies.cz/) (in Czech).

#### Contribution

After over a year of developing we've decided to publish the first version of the game.
From now on anyone is welcome to contribute. If we like your changes, we'll happily merge it.
If you spot a bug or have an idea for enhancement, write us an GitHub issue.

### Requirements

Python v. 3.8
We recommend to use virtual environment.

(Python version was raised from 3.7 to 3.8 for Pyglet 2)

To successfully run the project, run the script below. It will install all the requirements including additional libraries:
- [pyglet](https://bitbucket.org/pyglet/pyglet/wiki/Home) - the graphical library,
- [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://aiohttp.readthedocs.io/en/stable/) - asynchronous frameworks to run server and clients,
- [pyyaml](https://pyyaml.org/) - for reading the configuration files.
```
python -m pip install -r requirements.txt
```

For testing of this project we use [pytest](https://docs.pytest.org/en/latest/) framework. If you want to run the tests and don't have pytest on your computer, you can install it with the following command:
```
python -m pip install pytest
```

### The game

**How do you run the game?**

The game is playable through the network. Therefore it is divided into server and client parts. In order to play the game, you need to run the server first.
```
python server.py
```
You can choose a map to play directly from command line by writing the location of the JSON map as the optional argument `-m, --map-name`. For easier choice you can see the preview of maps in folder `maps/`.
The same way you can enter the number of players `-p, --players`. The current maps are prepared for the max. 8 players.

```
python server.py -m maps/belt_map.json -p 6
```

If you run server on a different computer than the clients, get the server's hostname and run clients with its value as the named argument `-h, --hostname`.
If you want to run both server and client/-s on the same computer, the default value `localhost` will be automatically set.
In order to see the game board with small players' avatars, use for example:
```
python client_receiver.py -h 192.168.10.1
```

And if you want to play with your own robot, there is a prepared interface which you can access through the welcome board.
There you can type a custom name for your robot and pick one from the available list.
```
python client_welcome_board.py -h 192.168.10.1
```
In case you want to get the first available robot with his factory name,
you can run the interface directly. This will skip the choice screen.
The list of factory names is available in `robots.yaml` (and can be customized if wanted).
In case you know which robot you want, use optional argument `-r, --robot-name` to pick him.
```
python client_interface.py -h 192.168.10.1 -r Bender
```
Get the list of all possible arguments by typing the client name and `--help`.
Note that the possibility to connect to server run on a different computer may be limited by your network provider.
In order to play the game, run as many interfaces as there are starting points on the map and at least one receiver.

**How do you win and how does the game round look like?**

Each player has one robot which can be programmed by cards. The goal is to collect all flags on the board in the increasing order. The first robot who collects all flags wins.

It is possible to play using both keyboard and the mouse. The keys are listed directly on the interface screen.

At the beginning of each round you get a random set of cards and by choosing cards for robot's slots you will set his moves for the round.
There is a time limit for choosing the cards. During the "choosing cards" part you can also put your robot to `Power Down` mode which means they won't make any actions by their own but they can be affected by other robots' actions.
Switching on `Power Down` also requires confirming the selection.
Once the "choosing cards" phase ends, the following steps will repeat 5 times:
1. The robots' card actions are performed in order of priority
2. The effects of tiles robots stand on are performed
3. Robots are shooting
4. If robot stands on the right flag tile, the flag is collected
5. If robot stands on the repair tile, the start position changes

After this phase is complete, the robots standing on the repair tile or in Power Down mode repair themselves and the next round begins.

### Tests

The tests are places in `tests/` folder. They are divided into separate files, eg. `test_effects.py`, `test_backend.py`, `test_loading.py`, covering respective modules.
`test_effects.py` reads the subfolders with test maps and commands. It executes the game on the background and asserts the robots performed the steps and their attributes were changed according to tile effects. For more details about testing framework see `tests/README-tests.md`.
`test_loading.py` also contains map validator (see map details below).

To run the tests, write the following command into the command line: `python -m pytest -v`

If you want to run only one of the testing files, add the name of the file after the command above.
The current tests handle only the game logic, not the network interfaces.

### Create your own map

Current maps were created in [Tiled](https://www.mapeditor.org/) map editor, version at least 1.2.1.
You can create your own map with the prepared tileset `development_tileset.json`.
When creating multiple-layered tiles, we strongly recommend to create the new layer for every kind of tiles, including the separate layers for lasers (horizontal, vertical) and walls (N, S, E, W).
The order of layers is checked by validator and must follow the pattern:
1. earth
2. one of the following: hole, start,
3. one of the following: repair, belt, gear
3. flag
4. pusher, laser, wall

### Automatic conversion from .SVG to .PNG

This project also contains a program `export_img.py` for automatic conversion of images in .SVG format to .PNG format.
The current version of the program uses [Inkscape](https://inkscape.org/) vector graphic editor so if you want to use this program, you need to install Inkscape first.  
To convert all images, run the `export_img.py` file from the root directory of the project. It will then export all images in .SVG to .PNG in all subdirectories.
