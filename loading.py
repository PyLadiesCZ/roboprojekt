"""
Loading module contains functions to load map file exported to json format from Tiled 1.2.
"""
from util import Tile, Direction
import json


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
    map_size = (data['width'], data['height'])
    for y in reversed(range(map_size[1])):
        for x in range(map_size[0]):
            coordinates.append((x, y))
    return coordinates, map_size


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


def get_types(data):
    """
    Get tile types.

    data: a dict created from decoded Tiled 1.2 JSON file

    Return a dictionary with modified tile ID as a key and type of tile as a value.
    """
    types = {}
    for json_tile in data['tilesets'][0]['tiles']:
        id = json_tile['id'] + data['tilesets'][0]['firstgid']
        types[id] = json_tile['type']
    return types


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


def get_board(map_name):
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
    data = get_data(map_name)
    paths = get_paths(data)
    coordinates, map_size = get_coordinates(data)
    types = get_types(data)

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
                tile = Tile(direction, paths[id], types[id])
                tiles.append(tile)
                board[coordinate] = tiles
    return board, map_size
