"""
Loading module contains functions to load map file exported to json format from Tiled 1.2.
"""
import json

from util_backend import Direction
from tile import create_tile_subclass


def get_map_data(map_name):
    """
    Return a dictionary of decoded JSON map file.

    map_name: a map of the game board created in Tiled 1.2 and saved as a JSON file
    """
    with open(map_name, encoding="utf-8") as map_file:
        map_data = json.load(map_file)
    return map_data


def get_coordinates(map_data):
    """
    Return a list of coordinates for individual tiles on the map.

    data: a dict created from decoded Tiled 1.2 JSON file

    Get the size of the game board and x, y vectors for each tile
    and creates a list of all tile coordinates, for example:
    [(0, 11), (0, 10), (0, 9), ..., (0, 0), (1, 11), (1, 10), ..., (11, 1), (11, 0)]
    Transformation with reversed is required as the JSON tiles are in an opposite direction.
    """
    coordinates = []
    for y in reversed(range(map_data["height"])):
        for x in range(map_data["width"]):
            coordinates.append((x, y))
    return coordinates


def get_tiles_data(map_data):
    """
    Get the tileset for the loaded map.
    If it is in separate file, load it from there.
    If the tileset is part of map data, load it directly.
    """
    # If the tileset is external, there will be ['source'] property present
    try:
        # This part is prepared for diferent tile sources, we don't support them now.
        # tileset_name = map_data['tilesets'][0]['source']
        # tileset_src = "maps/" + tileset_name

        tileset_src = "./maps/development_tileset.json"
        with open(tileset_src, encoding="utf-8") as tiles_file:
            tiles_data = json.load(tiles_file)
        loaded_tileset = tiles_data['tiles']

    # If the tileset is part of the map, the ['source'] property is not there,
    # therefore it throws KeyError. Use the map embedded tileset.
    except KeyError:
        loaded_tileset = map_data['tilesets'][0]['tiles']

    return loaded_tileset


def get_tiles_properties(map_data):
    """
    Get significant data from JSON tile fields.

    Take loaded data with tiles properties and return a tuple:
    tile types dict, tile's custom properties dict and names of images dict.
    """

    loaded_tileset = get_tiles_data(map_data)

    no_properties_tiles = {'ground', 'hole', 'wall'}
    types = {}
    properties = {}
    names = {}

    for json_tile in loaded_tileset:
        id = json_tile['id'] + map_data['tilesets'][0]['firstgid']

        # types as 'hole', 'pusher'
        types[id] = json_tile['type']

        # custom properties
        if types[id] not in no_properties_tiles:
            properties_list = []
            for property in json_tile['properties']:
                properties_list.append((property['name'], property['value']))
            properties[id] = dict(properties_list)
        else:
            properties[id] = {}

        # names of tile images
        name = types[id]
        if properties[id]:
            unique_properties = ''
            for property_name, property_value in properties[id].items():
                if property_value is True:
                    unique_properties = f"{unique_properties}_{property_name}"
                elif property_value is not False:
                    unique_properties = f"{unique_properties}_{property_value}"
            name = f"{name}{unique_properties}"
        names[id] = name

    return types, properties, names


def get_tile_id(tile_number):
    """
    Return tile ID.

    Transform tile_number to get tile ID that is equal to
    addiction of 'firstgid' value of tileset and tile ID stored in 'tilesets'
    part of JSON map format.
    The same ID that is used as a key in dict 'types' or 'properties'.
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


def board_from_data(map_data):
    """
    Create game board.

    Return dictionary of coordinates containing matching Tile objects.

    Create a board in format {(11, 0): [Tile, Tile, Tile], (11, 1): [Tile]...}.
    Tile object is created for every matching coordinates.
    For "empty" coordinates (not containing tiles) no objects are created.
    Tile object can appear many times on the same coordinates if the map contains more layers.
    Basic idea about dict comprehension used to create board can be found here:
    https://www.geeksforgeeks.org/python-dictionary-comprehension/
    """
    types, properties, names = get_tiles_properties(map_data)
    coordinates = get_coordinates(map_data)

    # create dictionary of coordinates where value is empty list for further transformation
    board = {coordinate: [] for coordinate in coordinates}
    for layer in map_data['layers']:

        # make tuple containing tile data and matching coordinates
        for tile_number, coordinate in zip(layer['data'], coordinates):
            id = get_tile_id(tile_number)
            tiles = board[coordinate]

            # if id == 0 there is empty space here, ergo don't create Tile object
            # otherwise add Tile object to the list of objects on the same coordinates
            if id != 0:
                direction = get_tile_direction(tile_number)
                tile = create_tile_subclass(direction, names[id], types[id], properties[id])
                tiles.append(tile)
                board[coordinate] = tiles
    return board


def get_board(map_name):
    """
    Create game board from provided data from JSON file.

    map_name: a map of the game board created in Tiled 1.2 and saved as a JSON file
    """
    map_data = get_map_data(map_name)
    return board_from_data(map_data)
