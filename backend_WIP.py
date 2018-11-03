#this file is still in progress

import json

# reading JSON file with testing map - one layer, no rotation
def get_data():
    map_name = "./maps/test_1.json"  # actual map path here
    with open(map_name, encoding="utf-8") as f:
        data = json.load(f)
    return data

# getting coordinates for individual tiles
def get_coordinates(data):
    # getting the size of the game board from json
    map_field_height = data['layers'][0]['height']
    map_field_width = data['layers'][0]['width']

    # creates map - list of x, y vectors 
    # transformation with reversed is required as the json tiles are in an opposite direction
    coordinates = []
    for y in reversed(range(map_field_height)):
        for x in range(map_field_width):       
            coordinates.append((x, y))
    return coordinates

# getting the list of tiles ID's
def get_ids(data):
    tiles = data['layers'][0]['data']
    firstgid = data['tilesets'][0]['firstgid']
    tile_ids = []
    for tile in tiles:
        tile = tile + firstgid
        tile_ids.append(tile)
    return tile_ids

# creates zip and transforms it to a dictionary of keys = (x, y) and values = [tile ID]
# if you're unsure about dict(), have a look at https://naucse.python.cz/2018/pyladies-brno-podzim/beginners/dict/
state = dict(zip(coordinates, tile_ids))

# get a dictionary with tile ID as a key and path to a real image as a value
#...
#...
#WIP
