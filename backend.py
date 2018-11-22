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


class Robot:
    def __init__(self, rotation, path, coordinates):
        self.rotation = rotation
        self.path = path
        self.coordinates = coordinates


class State:
    def __init__(self, board, robots):
        self.board = board
        self.robots = robots


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
    return number & 0xFFFFFF


def get_tile_rotation(number):
    return number >> (4*7)


def get_board(data):
    """
    Return dictionary of tiles together with path to image and its rotation.

    data: a dict created from decoded Tiled 1.2 JSON file
    coordinates: a list of coordinates of all tiles

    More about dictionaries: https://naucse.python.cz/2018/pyladies-brno-podzim/beginners/dict/
    """
    paths = get_paths(data)
    coordinates = get_coordinates(data)
    board = {coordinate: [] for coordinate in coordinates}
    rotation_dict = {0: 0, 10: 90, 12: 180, 6: 270}
    for layer in data['layers']:
        for data, coordinate in zip(layer['data'], coordinates):
            id = get_tile_id(data)
            tiles = board[coordinate]
            if id != 0:
                rotation_index = get_tile_rotation(data)
                rotation = rotation_dict[rotation_index]
                tile = Tile(rotation, paths[id])
                tiles.append(tile)
                board[coordinate] = tiles
    return board


def get_starting_coordinates(board):
    """
    Return a list with coordinates where are starting squares
    ...
    """
    starting_coordinates = []
    for key, list in board.items():
        for value in list:
            for i in range(9):
                if value.path == ("./img/squares/png/starting_square0{}.png".format(i)):
                    starting_coordinates.append(key)
    return starting_coordinates


def get_robot_paths():
    """
    Return a list with paths to robots images
    ...
    """
    robot_paths = []
    for path in Path('./img/robots_map/png/').iterdir():  # search image file
        robot_paths.append(path)
    return robot_paths


def get_robots_to_start(board):
    starting_coordinates = get_starting_coordinates(board)
    robot_paths = get_robot_paths()
    robots_start = []
    for coordinate in starting_coordinates:
        if robot_paths:
            path = random.choice(robot_paths)
            robot_paths.remove(path)
            robot = Robot(0, path, coordinate)
            robots_start.append(robot)
    return robots_start


def get_start_state(data):
    board = get_board(data)
    robots_start = get_robots_to_start(board)
    state = State(board, robots_start)
    return state
