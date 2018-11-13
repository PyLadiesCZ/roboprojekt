"""
Backend file contains functions for the game logic. 
"""

import json


class Tile:
    def __init__(self, id, rotation):
        self.id = id
        self.rotation = rotation


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
    map_field_height = data['layers'][0]['height']
    map_field_width = data['layers'][0]['width']
    coordinates = []
    for y in reversed(range(map_field_height)):
        for x in range(map_field_width):
            coordinates.append((x, y))
    return coordinates


def get_tiles(data):
    """
    Return the complete list of tiles.

    data: a dict created from decoded Tiled 1.2 JSON file
    Get the list of all tiles from the list "data" within the list "layers". 
    """

    rotation_dict = {0:0, 10:90, 12:180, 6:270}
    tilelist = {}
    for layer in data['layers']:
        tilelist_layer = []
        for data in layer['data']:
            real_tile = data & 0xFFFFFF
            rotation_index = data >> (4*7)
            rotation = rotation_dict[rotation_index]
            tile = Tile(real_tile, rotation)
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
    return state


def get_real_ids(data):
    """
    Return a dictionary with modified tile ID as a key and path to a real image as a value.

    data: a dict created from decoded Tiled 1.2 JSON file
    Create a dictionary where tile ID is modified with the number of the layer so it matches the number of the tile in the tilelist.
    """
    firstgid = data['tilesets'][0]['firstgid']
    real_images = {}
    for i in data['tilesets'][0]['tiles']:
        real_image_id = i['id']
        image_id = real_image_id + firstgid
        image_name = i['image']
        image_name = image_name[1:]  # unelegant way of removing ../ at the beginning of the path
        real_images[image_id] = image_name
    return real_images


