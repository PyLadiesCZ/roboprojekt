import pyglet
from pyglet.window import key
from interface import get_interface_state
from enum import Enum


window = pyglet.window.Window(768, 1024)
interface_state = get_interface_state()

# Interface element sprites
interface_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/interface.png'), x=0, y=0) # All Interface background
power_down_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/power.png'), x=186, y=854)
indicator_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/green.png'),  x=688, y=864) # Time indicator
card_background_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/card_bg.png')) # Universal cards background
select_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/card_cv.png')) # Gray overlay on selected cards
cursor_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/card_sl.png')) # Selection cursor
my_robot_sprite = pyglet.sprite.Sprite(pyglet.image.load(interface_state.robot_data.path), x=74, y=888) # My Robot img

lives_sprite = []
for i in range(3):
    x = 354 + i*46
    y = 864
    lives_sprite.append(pyglet.sprite.Sprite(pyglet.image.load('interface/png/life.png'), x, y))

flags_sprite = []
for i in range(8):
    x = 332 + i*48
    y = 928
    flags_sprite.append(pyglet.sprite.Sprite(pyglet.image.load('img/squares/png/flag_{}.png'.format(i+1)), x, y))

tokens_sprite = [] # Tokens of damage
for i in range(9):
    x = 676 + i*-70
    y = 768
    tokens_sprite.append(pyglet.sprite.Sprite(pyglet.image.load('interface/png/token.png'), x, y))

# Cards Sprites
cards_type_sprites = {
'u_turn' : pyglet.sprite.Sprite(pyglet.image.load('interface/png/u_turn.png')),
'back_up' : pyglet.sprite.Sprite(pyglet.image.load('interface/png/back.png')),
'left' : pyglet.sprite.Sprite(pyglet.image.load('interface/png/rotate_left.png')),
'right' : pyglet.sprite.Sprite(pyglet.image.load('interface/png/rotate_right.png')),
'move1' : pyglet.sprite.Sprite(pyglet.image.load('interface/png/move.png')),
'move2' : pyglet.sprite.Sprite(pyglet.image.load('interface/png/move.png')),
'move3' : pyglet.sprite.Sprite(pyglet.image.load('interface/png/move.png'))}


cards_table_coordinates = []
for i in range(5):
    x, y = 47, 384
    x = x + i* 144 # 144 space between cards
    cards_table_coordinates.append((x, y))
for i in range(4):
    x, y = 120, 224
    x = x + i* 144
    cards_table_coordinates.append((x, y))

cards_hand_coordinates = []
for i in range(5):
    x, y = 47, 576
    x = x + i* 144
    cards_hand_coordinates.append((x, y))


def draw_card(coordinate, card_type):
    x, y = coordinate

    # Draw universal background
    card_background_sprite.x = x
    card_background_sprite.y = y
    card_background_sprite.draw()

    # Draw card type
    name, value = card_type
    name = cards_type_sprites[name]
    name.x = x
    name.y = y
    name.draw()

    # Draw card value
    x = x + 70
    y = y + 118
    text = pyglet.text.Label(text = str(value), font_size = 14, x = x, y = y, anchor_x = 'right')
    text.draw()


@window.event
def on_draw():
    window.clear()

    # Interface background
    interface_sprite.draw()

    # Robot
    my_robot_sprite.draw()

    # Flags
    for sprite in flags_sprite[0:interface_state.robot_data.flags]:
        sprite.draw()

    # Robot lives
    for sprite in lives_sprite[0:interface_state.robot_data.lives]:
        sprite.draw()

    # Damage Tokens
    for sprite in tokens_sprite[0:interface_state.robot_data.damages]:
        sprite.draw()

    # CARDS
    # Cards table
    for i in range(0,(9-interface_state.robot_data.damages)):
        draw_card(cards_table_coordinates[i], interface_state.deal_cards[i]) # draw_card(coordinate, card_type)

    # Cards hand
    for i in interface_state.my_cards: # list of selected cards [((move3, 550), ...)]
        if i != None: # if selected card exist
            draw_card(cards_hand_coordinates[interface_state.my_cards.index(i)], i) # draw_card(coordinate, card_type)

    # Selected cards
    # if card is selected, selected card on the table is gray
    for i in interface_state.my_cards:
        if i != None:
            x, y = cards_table_coordinates[interface_state.deal_cards.index(i)]
            select_sprite.x = x
            select_sprite.y = y
            select_sprite.draw()

    # Cursor
    x, y = cards_hand_coordinates[interface_state.cursor_index]
    cursor_sprite.x = x
    cursor_sprite.y = y
    cursor_sprite.draw()

    # Power Down
    if interface_state.power_down == True:
        power_down_sprite.draw()


#CARD_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
CARD_KEYS= ["q", "w", "e", "r", "t", "a","s", "d", "f"]

@window.event
def on_text(text):

    if text in CARD_KEYS:
        #Select a card and take it in your "hand"
        #Selected card is in "GREEN" cursor
        deal_card_index = CARD_KEYS.index(text)
        interface_state.select_card(deal_card_index)

    # Return one card back on the teble
    if text == 'i':
        interface_state.return_card()

    # Return all cards back on the table
    if text == 'o':
        interface_state.return_cards()

    #Move  selector cursor to the right
    if text == 'm':
        interface_state.cursor_index_plus()

    #Move selector cursor to the left
    if text == 'n':
        interface_state.cursor_index_minus()

    #Put and take a Power Down token
    if text == 'p':
        interface_state.switch_power_down()

pyglet.app.run()
