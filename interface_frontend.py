import pyglet
from pyglet.window import key
from interface import get_interface_state, select_card, interface_index_minus, interface_index_plus, return_card, return_cards, switch_power_down
from enum import Enum


window = pyglet.window.Window(768, 1024)
interface_state = get_interface_state()

cards_table_row_1 = [(47, 384), 5, 144]
cards_table_row_2 = [(120, 224), 4, 144]
cards_row = [cards_table_row_1, cards_table_row_2]
cards_hand = [[(47, 576), 5, 144]]


interface_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/interface.png'), x=0, y=0)
power_down_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/power.png'), x=186, y=854)
indicator_sprite = pyglet.sprite.Sprite(pyglet.image.load('interface/png/green.png'),  x=688, y=864)

my_robot_sprite = pyglet.sprite.Sprite(pyglet.image.load(interface_state.robot_data.path), x=74, y=888)
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

tokens_sprite = []
for i in range(8):
    x = 676 + i*-70
    y = 768
    tokens_sprite.append(pyglet.sprite.Sprite(pyglet.image.load('interface/png/token.png'.format(i+1)), x, y))




img_type_paths = {'u_turn': 'interface/png/u_turn.png',
                    'back_up': 'interface/png/back.png',
                    'left': 'interface/png/rotate_left.png',
                    'right': 'interface/png/rotate_right.png',
                    'move1': 'interface/png/move.png',
                    'move2': 'interface/png/move.png',
                    'move3': 'interface/png/move.png',
                    'select': 'interface/png/card_cv.png',
                    'background':'interface/png/card_bg.png',
                    'cursor':'interface/png/card_sl.png'}


def get_cards_coordinates(cards_list):
    cards_coordinates = []
    for row in cards_list:
        for i in range(row[1]):
            x, y = row[0]
            x = x + i* row[2]
            cards_coordinates.append((x, y))
    return cards_coordinates


def create_cards_sprites(cards_type_list, coordinates):
    sprites = []

    for i, card_type in enumerate(cards_type_list, 0):
        if card_type != None:
            name, value = card_type
            x, y = coordinates[i]

            #Add a universal card background
            img = pyglet.image.load(img_type_paths['background'])
            sprite = pyglet.sprite.Sprite(img, x, y)
            sprites.append(sprite)

            #Add a card type symbol
            img = pyglet.image.load(img_type_paths[name])
            sprite = pyglet.sprite.Sprite(img, x, y)
            sprites.append(sprite)

            #Card value (number on the card)
            x = x + 70
            y = y + 118
            text = pyglet.text.Label(text = str(value), font_size = 14, x = x, y = y, anchor_x = 'right')
            sprites.append(text)
    return sprites


def create_one_sprite(type, coordinate):
    x, y = coordinate
    img = pyglet.image.load(img_type_paths[type])
    sprite = pyglet.sprite.Sprite(img, x, y)
    return sprite


def draw_interface(sprites):
    for tile_sprite in sprites:
        tile_sprite.draw()

@window.event
def on_draw():
    window.clear()

    #Interface background
    interface_sprite.draw()

    #Robot
    my_robot_sprite.draw()

    #Flags
    for sprite in flags_sprite[0:interface_state.robot_data.flagcount]:
        sprite.draw()

    #Robot lives
    for sprite in lives_sprite[0:interface_state.robot_data.lifecount]:
        sprite.draw()

    #Damage Tokens
    for sprite in tokens_sprite[0:interface_state.robot_data.damagecount]:
        sprite.draw()


    #Cards
    draw_interface(create_cards_sprites(interface_state.deal_cards, cards_table_coordinates))
    draw_interface(create_cards_sprites(interface_state.my_cards, cards_hand_coordinates))
    print(cards_table_coordinates)
    for i in interface_state.my_cards:
        if i != None:
            create_one_sprite('select', cards_table_coordinates[interface_state.deal_cards.index(i)]).draw()
    create_one_sprite('cursor', cards_hand_coordinates[interface_state.cursor_index]).draw()

    #Power Down
    if interface_state.power_down == True:
        power_down_sprite.draw()



#CARD_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
CARD_KEYS= ["q", "w", "e", "r", "t", "a","s", "d", "f"]
cards_table_coordinates = get_cards_coordinates(cards_row)
cards_hand_coordinates = get_cards_coordinates(cards_hand)



@window.event
def on_text(text):
    print(text)

    #Put and take a Power Down token
    if text == 'p':
        switch_power_down(interface_state)

    if text in CARD_KEYS:
        #Select a card and take it in your "hand"
        #Selected card is in "GREEN" cursor
        deal_card_index = CARD_KEYS.index(text)

        select_card(deal_card_index, interface_state)


    # selected cards back to the "table"
    if text == 'o':
        return_cards(interface_state)
    # one selected card back to the "table"
    if text == 'i':
        return_card(interface_state)

    #Move  selector cursor to the right
    if text == 'm':
        interface_index_plus(interface_state)

    #Move selector cursor to the left
    if text == 'n':
        interface_index_minus(interface_state)

# def tick(dt):
#     pass
#
# pyglet.clock.schedule_interval(tick, 1/60)

pyglet.app.run()
