import json
import pyglet

map_name = "./maps/test_1.json"  # change the map here!!!

# reading JSON file with my map - one layer, no rotation
with open(map_name, encoding="utf-8") as f:
    contents = f.read()
data = json.loads(contents)

# json file holds the information about the size of the game board
map_field_height = data['layers'][0]['height']
map_field_width = data['layers'][0]['width']

TILE_HEIGHT = data['tileheight']
TILE_WIDTH = data['tilewidth']
BOARD_WIDTH = TILE_WIDTH*map_field_width
BOARD_HEIGHT = TILE_HEIGHT*map_field_height

# creates 12x12 map - list of x, y vectors (11, 11) to (0, 0)
# transformation with reversed is required as the json tiles are in an opposite direction
list_of_xys = []
for y in reversed(range(map_field_height)):
    for x in range(map_field_width):       
        list_of_xys.append((x, y))        

# let's get the list of tiles ID's!
json_tiles = data['layers'][0]['data']  

# let's get the right tiles numbers (-1)!
tiles_without_layer = []
for i in json_tiles:
    i -= 1 #gets real tile ID
    tiles_without_layer.append(i)
    
# creates zip and transforms it to a dictionary of keys = (x, y) and values = [tile ID]
# if you're unsure about dict(), have a look at 
# https://naucse.python.cz/2018/pyladies-brno-podzim/beginners/dict/
state = dict(zip(list_of_xys, tiles_without_layer))

# creates a dictionary, where key is tile ID and value path to a real image
json_dict = {}
for i in range(len(data['tilesets'][0]['tiles'])):
    image_id = data['tilesets'][0]['tiles'][i]['id']
    image_name = data['tilesets'][0]['tiles'][i]['image']
    image_name = image_name[1:] # unelegant way of removing ../ at the beginning of the path
    json_dict[image_id] = image_name

def list_tiles():
    imgs = []
    for key in state:
        if state[key] in json_dict: 
            img = pyglet.image.load(json_dict[state[key]])  
            # pin the img to the middle       
            img.anchor_x = img.width // 2   
            img.anchor_y = img.height // 2   
            # coordinates where to draw the img 
            x, y = key
            tile_x = x*TILE_WIDTH  
            tile_y = y*TILE_HEIGHT
            img = pyglet.sprite.Sprite(img, x=img.anchor_x+tile_x, y=img.anchor_y+tile_y)        
            imgs.append(img)
    return imgs


window = pyglet.window.Window(width=BOARD_WIDTH, height=BOARD_HEIGHT)
tiles = list_tiles()

@window.event
def on_draw():
    window.clear()
    
    for tile in tiles:
        tile.draw()

pyglet.app.run()    
