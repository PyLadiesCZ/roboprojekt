"""
Backend file contains functions for the game logic.
"""

import json
from pathlib import Path
import random

class Tile:
    def __init__(self, rotation, path):
        self.rotation = rotation
        self.path = path

    def __repr__(self):
        return "<Tile> {} {}>".format(self.rotation, self.path)

class Robot:
    def __init__(self, rotation, path, coordinates):
        self.rotation = rotation
        self.path = path
        self.coordinates = coordinates

    def move_robot(self, distance):
        """
        this method calculates new coordinates of a robot
        """
        
        (x, y) = self.coordinates
        
        if self.rotation == 0:
            y += distance 
        elif self.rotation == 90:
            x += distance
        elif self.rotation == 180:
            y -= distance
        elif self.rotation == 270:
            x -= distance
            
        self.coordinates = (x, y)
    

    def __repr__(self):
        return "<Robot> {} {} {}>".format(self.rotation, self.path, self.coordinates)

class State:
    def __init__(self, board, robots):
        self.board = board
        self.robots = robots

    def __repr__(self):
        return "<State> {} {}>".format(self.board, self.robots)

def get_data(map_name):
    """
    Return decoded JSON map file as a dictionary.

    map_name: a map of the game board created in Tiled 1.2 and saved as JSON file
    json.load() turns JSON encoded data into Python objects
    """
    with open(map_name, encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_coordinates(data):
    """
    Return a list of coordinates for individual tiles on the map.

    data: a dict created from decoded Tiled 1.2 JSON file
    Get the size of the game board and x, y vectors for each tile and creates a list of all tile coordinates, for example:
    [(0, 11), (0, 10), (0, 9), ..., (0, 0), (1, 11), (1, 10), ..., (11, 1), (11, 0)]
    Transformation with reversed is required as the JSON tiles are in an opposite direction.
    """
    coordinates = []
    for y in reversed(range(data['layers'][0]['height'])):
        for x in range(data['layers'][0]['width']):
            coordinates.append((x, y))
    return coordinates


def get_paths(data):
    """
    Return a dictionary with modified tile ID as a key and path to a real image as a value.

    data: a dict created from decoded Tiled 1.2 JSON file
    Create a dictionary where tile ID is modified with the number of the layer so it matches the number of the tile in the tilelist.
    """
    paths = {}
    for i in data['tilesets'][0]['tiles']:
        image_id = i['id'] + data['tilesets'][0]['firstgid']
        image_path = i['image']
        image_path = image_path[1:]  # unelegant way of removing ../ at the beginning of the path
        paths[image_id] = image_path
    return paths


def get_tile_id(number):
    """
    Get actual tile ID.

    Transform number to return the one corresponding with ID's stored in "tilesets" part of JSON map format.
    """
    return number & 0xFFFFFF


def get_tile_rotation(number):
    """
    Get actual tile rotation.

    Transform number to return the value of degrees in which the tile is rotated.
    """
    rotation_dict = {0: 0, 10: 90, 12: 180, 6: 270}
    rotation_number = number >> (4*7)

    return rotation_dict[rotation_number]


def get_board(data):
    """
    Get dictionary of coordinates containing matching Tile objects.

    data: a dict created from decoded Tiled 1.2 JSON file

    Create a board in format {(11, 0): [Tile, Tile, Tile], (11, 1): [Tile]...}.
    Tile object is created for every matching coordinates.
    For "empty" coordinates (not containing tiles) no objects are created.
    Tile object can appear many times on the same coordinates if the map contains more layers.
    More about dictionaries: https://naucse.python.cz/2018/pyladies-brno-podzim/beginners/dict/
    """
    paths = get_paths(data)
    coordinates = get_coordinates(data)

    # create dictionary of coordinates where value is empty list for further transformation
    board = {coordinate: [] for coordinate in coordinates}
    for layer in data['layers']:

        # make tuple containing tile data and matching coordinates
        for data, coordinate in zip(layer['data'], coordinates):
            id = get_tile_id(data)
            tiles = board[coordinate]

            # if id == 0 there is empty space here, ergo don't create Tile object
            # otherwise add Tile object to the list of objects on the same coordinates
            if id != 0:
                rotation = get_tile_rotation(data)
                tile = Tile(rotation, paths[id])
                tiles.append(tile)
                board[coordinate] = tiles
    return board


def get_starting_coordinates(board):
    """
    Get a list with coordinates of starting squares.

    board: dictionary returned by get_board().
    Find the objects which are starting squares (matching attribute path of Tile object),
    then add the key of those squares to the list.
    """
    starting_coordinates = []
    for key, list in board.items():
        for value in list:
            # range(9) because there may be max. 8 starting squares
            for i in range(9):
                if value.path == ("./img/squares/png/starting_square0{}.png".format(i)):
                    starting_coordinates.append(key)
    return starting_coordinates


def get_robot_paths():
    """
    Get a list of paths to robots images.

    Using pathlib.Path library add all the files in given directory to the list.
    Ex. [PosixPath('img/robots_map/png/MintBot.png'), PosixPath('img/robots_map/png/terka_robot_map.png')].
    """
    robot_paths = []
    for path in Path('./img/robots_map/png/').iterdir():  # search image file
        robot_paths.append(path)
    return robot_paths


def get_robots_to_start(board):
    """
    Get list of robots on the starting squares of the board.

    board: dictionary returned by get_board().

    Initialize Robot objects on the starting square coordinates with random choice of robot's avatar on particular square.
    Once the robot is randomly chosen, it is removed from the list (it cannot appear twice on the board).
    On the beginning all the Robot objects have implicit 0 degree rotation.
    """
    starting_coordinates = get_starting_coordinates(board)
    robot_paths = get_robot_paths()
    robots_start = []
    for coordinate in starting_coordinates:

        # Condition to assure no exception in case robot_paths is shorter than coordinate's list
        if robot_paths:
            path = random.choice(robot_paths)
            robot_paths.remove(path)
            robot = Robot(0, path, coordinate)
            robots_start.append(robot)
    return robots_start


def get_start_state(data):
    """
    Get starting state of game.

    data: a dict created from decoded Tiled 1.2 JSON file

    Create board and robots on starting squares, initialize State object containing both Tile and Robot object.
    Return State object.
    """
    board = get_board(data)
    robots_start = get_robots_to_start(board)
    state = State(board, robots_start)
    return state
