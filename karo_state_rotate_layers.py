import json
import pyglet

map_name = "./maps/test_3.json"  # change the map here!!!

# reading JSON file with my map - one layer, no rotation
with open(map_name, encoding="utf-8") as f:
    contents = f.read()
data = json.loads(contents)

# json file holds the information about the size of the game board
field_height = data['layers'][0]['height']
field_width = data['layers'][0]['width']

TILE_HEIGHT = data['tileheight']
TILE_WIDTH = data['tilewidth']
WIDTH = TILE_WIDTH*field_width
HEIGHT = TILE_HEIGHT*field_height

# creates 12x12 map - list of x, y vectors (11, 11 to 0, 0)
# transformation with reversed is required as the json tiles are in an opaque direction
list_of_xys = []
for y in reversed(range(field_height)):
    for x in range(field_width):       
        list_of_xys.append((x, y))        

#let's get directions!
direction_dict = {0: 0, 10: 90, 12: 180, 6: 270}

#let's get the layers!
layers = []
for i in range(len(data['layers'])):
    # gets the list of tiles numbers 
    json_list_of_tiles = data['layers'][i]['data']
  
    # let's get the right tiles numbers!
    list_of_tiles_without_layer = []
    for j in json_list_of_tiles:
        tile_effects = []  # empty list to create two instances for one tile - tile ID, effect
        tile_direction = j>>(4*7) #gets rotation
        j = j & 0xFFFFFFF  #gets decimal value
        j -= 1 #gets real tile ID
        tile_effects.append(j)
        tile_effects.append(tile_direction)
        list_of_tiles_without_layer.append(tile_effects)
    
    # creates zip to transform to a dictionary
    my_zip = zip(list_of_xys, list_of_tiles_without_layer)
    
    # creates state: dictionary of keys = x, y tuples and values = ID of field 
    state = dict(my_zip)

    layers.append(state)
    
json_dict = {}
for i in range(len(data['tilesets'][0]['tiles'])):
    image_id = data['tilesets'][0]['tiles'][i]['id']
    image_name = data['tilesets'][0]['tiles'][i]['image']
    image_name = image_name[1:] # unelegant way of removing ../ at the beginning of the path
    json_dict[image_id] = image_name

def draw_tiles():
    img_dict = []
    for layer in layers:
        for key in layer:
            if layer[key][0] in json_dict: 
                img = pyglet.image.load(json_dict[layer[key][0]])
                # pin the img to the middle       
                img.anchor_x = img.width // 2
                img.anchor_y = img.height // 2
                # get coordinates where to draw the img 
                x, y = key
                tile_x = x*TILE_WIDTH
                tile_y = y*TILE_HEIGHT
                img = pyglet.sprite.Sprite(img, x=img.anchor_x+tile_x, y=img.anchor_y+tile_y)
                img.rotation = direction_dict[layer[key][1]] 
                img_dict.append(img)
    return img_dict

window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

tiles = draw_tiles()

@window.event
def on_draw():
    window.clear()
    
    for tile in tiles:
        tile.draw()

pyglet.app.run()    










