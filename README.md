# RoboProject
*Advanced PyLadies CZ Course*

This course was created primarilly for those who succesfully passed the PyLadies beginner courses and want to continue with Python via "real" project. It should show participants the process of software development from the very basics, and enable them to try it on their own. It is focused on team cooperation, using Python for real tasks, working with Git and GitHub, showing best practices and trying various useful tools. 

The assignment of this project is transforming board game RoboRally to computer version so the final result should be working playable computer game.

You can follow the progress on our [blog](https://roboprojekt.pyladies.cz/).

Please note that the game is still in progress and the current version is not playable.

### Requirements

Python v.3.x
We recommend to use virtual environment.

To succesfully run the project, run the script below. It will install all the requirements including [pyglet](https://bitbucket.org/pyglet/pyglet/wiki/Home) library.
```
python -m pip install -r requirements.txt
```

For testing of this project we use [pytest](https://docs.pytest.org/en/latest/) framework. If you want to run the tests and don't have pytest on your computer, you can install it with the following command:
```
python -m pip install pytest
```

### The game

**How do you run the game?**

To run the game you need to open the `game.py` module in the command line:
```
python game.py
```

**How do you win and how does the game round look like?**

Each player has one robot which can be programmed by cards. The goal is to collect all flags on the board in the increasing order. The first robot who collects all flags wins.

At the beginning of each round you get a random set of cards and by choosing cards for robot's slots you will set his moves for the round.
There is a time limit for choosing the cards. During the "choosing cards" part you can also put your robot to `Power Down` mode which means they won't make any actions by their own but they can be affected by other robots' actions. 
Once the "choosing cards" phase ends, the following steps will repeat 5 times:
1. The robots' card actions are performed in order of priority
2. The effects of tiles robots stand on are performed
3. Robots are shooting
4. If robot stands on the right flag tile, the flag is collected
5. If robot stands on the repair tile, the start position changes

After this phase is complete, the robots standing on the repair tile or in Power Down mode repair themselves and the next round begins.

### Tests

Currently, the tests are divided into two separate files, `test_backend.py` and `test_loading.py`, covering respective modules. The second file also contains map validator (see map details below).

To run the tests, write the following command into the command line: `python -m pytest -v` 

If you want to run only one of the testing files, add the name of the file after the command above. 

### Create your own map

Current maps were created in [Tiled](https://www.mapeditor.org/) map editor. 
You can create your own map by using one of the prepared maps as a template as it contains the tileset used for the game.
Or you can export the tileset and import it into the blank Tiled project.
When creating multiple-layered tiles, keep the following order of layers:
1. earth
2. one of the following: hole, start, repair, belt, turn
3. flag
4. laser, wall, pusher

Part of the test suite is a map validator which checks the order of tile layers.

### Automatic conversion from .SVG to .PNG

This project also contains a program `export_img.py` for automatic conversion of images in .SVG format to .PNG format. 
The current version of the program uses [Inkscape](https://inkscape.org/) vector graphic editor so if you want to use this program, you need to install Inkscape first.  
To convert all images, run the `export_img.py` file from the root directory of the project. It will then export all images in .SVG to .PNG in all subdirectories.

