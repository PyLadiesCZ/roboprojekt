"""
Backend file contains functions for the game logic.
"""

import json
from pathlib import Path

class Tile:
    def __init__(self, rotation, path):
        self.rotation = rotation
        self.path = path


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


def get_tiles(data):
    """
    Return dictionary of tiles together with path to image and its rotation.

    data: a dict created from decoded Tiled 1.2 JSON file
    """
    paths = get_paths(data)
    rotation_dict = {0:0, 10:90, 12:180, 6:270}
    tilelist = {}
    for layer in data['layers']:
        tilelist_layer = []
        for data in layer['data']:
            id = data & 0xFFFFFF
            if id == 0:
                tile = Tile(0, 0)
            else:
                rotation_index = data >> (4*7)
                rotation = rotation_dict[rotation_index]
                tile = Tile(rotation, paths[id])
            tilelist_layer.append(tile)
        tilelist[layer['id']] = tilelist_layer
    return tilelist

def get_coordinate_dict(coordinates, tilelist):
    """
    Return the game board state.

    coordinates: a list of coordinates of all tiles
    tilelist: a list of all tiles
    More about dictionaries: https://naucse.python.cz/2018/pyladies-brno-podzim/beginners/dict/
    """
    state = {}
    for layer in tilelist:
        state[layer] = dict(zip(coordinates, tilelist[layer]))
    return state #{1: {(0, 11): <backend.Tile object at 0x7f21f93abfd0>,


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
    return paths #{1: './img/squares/png/ground.png',

def get_starting_coordinate(state):
    """
    Return a list with coordinates where are starting square
    ...
    """
    starting_coordinate = []
    for list in state.items():
        for key, value in list[1].items():
            for i in range(9):
                if value.path == (f"./img/squares/png/starting_square0{i}.png"):
                    starting_coordinate.append(key)
    return(starting_coordinate)

def get_robot_path():
    robot_path = []
    for robot in Path('./img/robots_map/png/').iterdir():
        robot_path.append(robot)
    return robot_path
