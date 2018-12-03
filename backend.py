"""
Backend file contains functions for the game logic.
"""

import json
from pathlib import Path
import random
from enum import Enum

class Tile:
    def __init__(self, direction, path):
        self.direction = direction
        self.path = path

    def __repr__(self):
        return "<Tile> {} {}>".format(self.direction, self.path)


class Robot:
    def __init__(self, direction, path, coordinates):
        self.direction = direction
        self.path = path
        self.coordinates = coordinates

    def __repr__(self):
        return "<Robot> {} {} {}>".format(self.direction, self.path, self.coordinates)

    def walk(self, distance):
        """
        Move a robot to new coordinates based on its direction.
        """

        self.move(self.direction, distance)

    def move(self, direction, distance):
        """
        Move a robot to new coordinates according to direction of the move.
        """

        (x, y) = self.coordinates
        (new_x, new_y) = direction.vector
        x = x + (new_x * distance)
        y = y + (new_y * distance)

        self.coordinates = (x, y)

    def rotate(self, where_to):
        """
        Rotate robot according to a given direction.
        """

        self.direction = self.direction.get_new_direction(where_to)


class State:
    def __init__(self, board, robots):
        self.board = board
        self.robots = robots

    def __repr__(self):
        return "<State> {} {}>".format(self.board, self.robots)


class Direction(Enum):
    N = 0, (0, +1), 0
    E = 90, (+1, 0), 1
    S = 180, (0, -1), 2
    W = 270, (-1, 0), 3

    def __new__(cls, keycode, vector, tile_property):
        """
        Get attributes value and vector of the given Direction class values.

        Override standard enum __new__ method.
        vector: new coordinates (where the robot goes to)
        tile_property: map tile property: value (custom - added in Tiled).
        Makes it possible to change vector and tile_property when the object is rotated.
        With degrees change (value) there comes the coordinates (vector) change and tile_property.
        """
        obj = object.__new__(cls)
        obj._value_ = keycode
        obj.vector = vector
        obj.tile_property = tile_property
        return obj

    def get_new_direction(self, where_to):
        """
        Get new direction of given object.

        Change attribute direction according to argument where_to, passed from TDB class DirectionOfRotation.
        """
        if where_to == "right":
            return Direction((self.value + 90) % 360)
        if where_to == "left":
            return Direction((self.value + 270) % 360)
        if where_to == "upside_down":
            return Direction((self.value + 180) % 360)


def get_data(map_name):
    """
    Return a dictionary of decoded JSON map file.

    map_name: a map of the game board created in Tiled 1.2 and saved as a JSON file
    """
    with open(map_name, encoding="utf-8") as map_file:
        data = json.load(map_file)
    return data


def get_coordinates(data):
    """
    Return a list of coordinates for individual tiles on the map.

    data: a dict created from decoded Tiled 1.2 JSON file

    Get the size of the game board and x, y vectors for each tile
    and creates a list of all tile coordinates, for example:
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
    Get paths to tiles images.

    data: a dict created from decoded Tiled 1.2 JSON file

    Return a dictionary with modified tile ID as a key and path to file
    of the image as a value.

    Create a dictionary where tile ID is modified with the number of the
    tileset used in Tiled 1.2, so it matches the tile number in the tilelist.
    """
    paths = {}
    for json_tile in data['tilesets'][0]['tiles']:
        id = json_tile['id'] + data['tilesets'][0]['firstgid']
        path = json_tile['image']
        path = path[1:]  # unelegant way of removing ../ at the beginning of the path
        paths[id] = path
    return paths


def get_tile_id(tile_number):
    """
    Return tile ID.

    Transform tile_number to get tile ID that is equal to
    addiction of 'firstgid' value of tileset and tile ID stored in 'tilesets'
    part of JSON map format. The same ID that is used as a key in dict 'paths'.
    """
    return tile_number & 0xFFFFFF


def get_tile_direction(tile_number):
    """
    Return tile direction.

    Transform tile_number to get the value of tile's direction in degrees.
    """
    direction_dict = {0: Direction.N, 10: Direction.E, 12: Direction.S, 6: Direction.W}
    direction_number = tile_number >> (4*7)

    return direction_dict[direction_number]


def get_board(data):
    """
    Create game board from provided data from JSON file.

    data: a dict created from decoded Tiled 1.2 JSON file

    Return dictionary of coordinates containing matching Tile objects.

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
        for tile_number, coordinate in zip(layer['data'], coordinates):
            id = get_tile_id(tile_number)
            tiles = board[coordinate]

            # if id == 0 there is empty space here, ergo don't create Tile object
            # otherwise add Tile object to the list of objects on the same coordinates
            if id != 0:
                direction = get_tile_direction(tile_number)
                tile = Tile(direction, paths[id])
                tiles.append(tile)
                board[coordinate] = tiles
    return board


def get_starting_coordinates(board):
    """
    Get starting coordinates for robots.

    board: dictionary returned by get_board().

    Return a list with coordinates of starting tiles.

    Find the objects which are starting tiles (matching attribute path of Tile object),
    then add coordinate of those tiles to the list of starting coordinates.
    """
    starting_coordinates = []
    for coordinate, tiles in board.items():
        for tile in tiles:
            # range(9) because there may be max. 8 starting squares
            for i in range(9):
                if tile.path == ("./img/squares/png/starting_square0{}.png".format(i)):
                    starting_coordinates.append(coordinate)
    return starting_coordinates


def get_robot_paths():
    """
    Return a list of paths to robots images.

    Using pathlib.Path library add all the files in given directory to the list.
    Ex. [PosixPath('img/robots_map/png/MintBot.png'), PosixPath('img/robots_map/png/terka_robot_map.png')].
    """
    robot_paths = []
    for robot_path in Path('./img/robots_map/png/').iterdir():  # search image file
        robot_paths.append(robot_path)
    return robot_paths


def get_robots_to_start(board):
    """
    Place robots on starting tiles.

    board: dictionary returned by get_board()

    Return list of robots on the starting tiles of the board.

    Initialize Robot objects on the starting tiles coordinates with random
    choice of robot's avatar on particular tile.
    Once the robot is randomly chosen, it is removed from the list
    (it cannot appear twice on the board).
    On the beginning all the Robot objects have implicit 0 degree direction.
    """
    starting_coordinates = get_starting_coordinates(board)
    robot_paths = get_robot_paths()
    robots_start = []
    for coordinate in starting_coordinates:

        # Condition to assure no exception in case robot_paths is shorter
        # than coordinate's list
        if robot_paths:
            path = random.choice(robot_paths)
            robot_paths.remove(path)
            robot = Robot(Direction.N, path, coordinate)
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
