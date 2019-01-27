# RoboProject
*Advanced PyLadies CZ Course*

This course was created primarilly for those who succesfully passed the PyLadies beginner courses and want to continue with Python via "real" project. It should show participants the process of software development from the very basics, and enable them to try it on their own. It is focused on team cooperation, using Python for real tasks, working with Git and GitHub, showing best practices and trying various useful tools. 

The assignment of this project is transforming board game RoboRally to computer version so the final result should be working playable computer game.

You can follow the progress on our [blog](https://roboprojekt.pyladies.cz/).

### Requirements

Python v.3.x
We recommend to use virtual environment.

To succesfully run the project you need to install [pyglet](https://bitbucket.org/pyglet/pyglet/wiki/Home) library.
```
python -m pip install pyglet
```

For testing of this project we use [pytest](https://docs.pytest.org/en/latest/) framework. If you don't have it on your computer, you can install it with the following command:
```
python -m pip install pytest
```

### The game

**How do you win and how does the game round look like?**

Each player has one robot which can be programmed by cards. The goal is to collect all flags on the board in the increasing order. The first robot who collects all flags wins.

At the beginning of each round you get a random set of cards and by choosing cards for robot's slots you will set his moves for the round.
There is a time limit for choosing the cards. During the "choosing cards" part you can also put your robot to `Power Down` mode which means they won't make any actions by their own but they can be affected by other robots' actions. 
Once the "choosing cards" phase ends, the following steps will repeat 5 times:
1. The robots' card actions are resolved in order of priority
2. The effects of tiles robots stand on are resolved
3. Robots are shooting
4. If robot stands on the flag tile, the flag is collected
5. If robot stands on the repair tile, the start position changes

After this phase is complete, the robots standing on the repair tile or in Power Down mode repair themselves and the next round begins.

### Tests

Currently, the tests are divided into two separate files, `test_backend.py` and `test_loading.py`, covering respective modules. The second file also contains map validator (see map details below).

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
