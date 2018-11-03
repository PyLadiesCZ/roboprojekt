#this file is still in progress

import json

map_name = "./maps/test_1.json"  # actual map path here

# reading JSON file with testing map - one layer, no rotation
def get_data(map_name):
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

# getting the list of json tiles
def get_tiles(data):
    tilelist = data["layers"][0]["data"]
    return tilelist

# creates zip and transforms it to a dictionary of keys = (x, y) and values = [tiles]
# if you're unsure about dict(), have a look at https://naucse.python.cz/2018/pyladies-brno-podzim/beginners/dict/
state = dict(zip(coordinates, tilelist))

# getting a dictionary with modified tile ID as a key and path to a real image as a value
def get_real_ids(data):
    firstgid = data['tilesets'][0]['firstgid']
    real_images = {}
    for i in range(len(data['tilesets'][0]['tiles'])):
        real_image_id = data['tilesets'][0]['tiles'][i]['id']
        image_id = real_image_id + firstgid
        image_name = data['tilesets'][0]['tiles'][i]['image']
        image_name = image_name[1:] # unelegant way of removing ../ at the beginning of the path
        real_images[image_id] = image_name
    return real_images

#WIP
