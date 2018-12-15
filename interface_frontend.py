import pyglet
from pyglet.window import key
from interface import get_interface_state
from enum import Enum


window = pyglet.window.Window(768, 1024)
interface_state = get_interface_state()

cards_row_1 = [(47, 384), 5, 144]
cards_row_2 = [(120, 224), 4, 144]
cards_row = [cards_row_1, cards_row_2]
my_cards = [[(47, 576), 5, 144]]
selected_cards = []

CARD_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]


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


class InterfaceData(Enum):
    interface =(0, 0),1, 0,'interface/png/interface.png'
    lives = (354, 864), 3, 46, 'interface/png/life.png'
    indicator = (688, 864), 1, 0, 'interface/png/green.png'
    flags = (332, 928), 8, 48, 'img/squares/png/flag_{}.png'
    tokens = (676, 768), 10, -70, 'interface/png/token.png'
    power_down = (186, 854), 1, 0, 'interface/png/power.png'
    my_robot = (74, 888), 1, 0, interface_state.robot_data.path

    def __init__(self, first_coordinates, elements_count, space, path):
        self.first_coordinates = first_coordinates
        self.elements_count = elements_count
        self.space = space
        self.path = path


def get_cards_coordinates(cards_list):
    cards_coordinates = []
    for row in cards_list:
        for i in range(row[1]):
            x, y = row[0]
            x = x + i* row[2]
            cards_coordinates.append((x, y))
    return cards_coordinates

cards_table_coordinates = get_cards_coordinates(cards_row)
cards_hand_coordinates = get_cards_coordinates(my_cards)
cursor_coordinates = []


def cards_sprites(cards_type_dict, coordinates):
    sprites = []
    for i, card_type in enumerate(cards_type_dict, 0):

        name, value = card_type
        x, y = coordinates[i]

        """
        Add a universal card background
        """
        img = pyglet.image.load(img_type_paths['background'])
        sprite = pyglet.sprite.Sprite(img, x, y)
        sprites.append(sprite)

        """
        Add a card type symbol
        """

        img = pyglet.image.load(img_type_paths[name])
        sprite = pyglet.sprite.Sprite(img, x, y)
        sprites.append(sprite)

        """
        Card value (number on the card)
        """
        x = x + 70
        y = y + 118
        text = pyglet.text.Label(text = str(value), font_size = 14, x = x, y = y, anchor_x = 'right')
        sprites.append(text)
    return sprites


def block_card(type, coordinates):
    sprites = []
    for coordinate in coordinates:
        x, y = coordinate
        img = pyglet.image.load(img_type_paths[type])
        sprite = pyglet.sprite.Sprite(img, x, y)
        sprites.append(sprite)
    return sprites


def create_sprites(element):
    sprites = []
    for i in range(element.elements_count):
        x, y = element.first_coordinates
        x = x + i * element.space
        img = pyglet.image.load(element.path.format(i+1))
        sprite = pyglet.sprite.Sprite(img, x, y)
        sprites.append(sprite)
    return sprites


def draw_interface(sprites):
    for tile_sprite in sprites:
        tile_sprite.draw()


def interface():
    """
    Interface
    """
    draw_interface(create_sprites(InterfaceData.interface))

    """
    Robot
    """
    draw_interface(create_sprites(InterfaceData.my_robot))

    draw_interface(create_sprites(InterfaceData.lives)[0:interface_state.robot_data.lifecount])
    draw_interface(create_sprites(InterfaceData.tokens)[0:interface_state.robot_data.damagecount])
    draw_interface(create_sprites(InterfaceData.flags)[0:interface_state.robot_data.flagcount])

    """
    Cards
    """
    draw_interface(cards_sprites(interface_state.deal_cards, cards_table_coordinates))
    draw_interface(cards_sprites(interface_state.my_cards, cursor_coordinates))

    draw_interface(block_card('select', selected_cards))
    draw_interface(block_card('cursor', [cards_hand_coordinates[interface_state.select_cursor]]))

    """
    Power Down
    """
    if interface_state.power_down == True:
        draw_interface(create_sprites(InterfaceData.power_down))


@window.event
def on_draw():
    window.clear()
    interface()


@window.event
def on_text(text):
    print(text)

    if text == 'p':
        """
        Put and take a Power Down token
        """
        if interface_state.power_down == False:
            interface_state.power_down = True
        else:
            interface_state.power_down = False

    if text in CARD_KEYS:
        """
        Select a card and take it in your "hand"

        Selected card is in "GREEN" cursor
        """
        index = CARD_KEYS.index(text)
        if len(interface_state.my_cards) < 5:
            if interface_state.deal_cards[index] not in interface_state.my_cards:
                interface_state.my_cards.append(interface_state.deal_cards[index])
                cursor_coordinates.append(cards_hand_coordinates[interface_state.select_cursor])
                if interface_state.select_cursor < 4:
                    interface_state.select_cursor += 1
                selected_cards.append(cards_table_coordinates[index])


    if text == 'm':
        """
        Move  selector cursor to the right
        """
        print(interface_state.select_cursor)
        if interface_state.select_cursor < 4:
            interface_state.select_cursor += 1
    if text == 'n':
        """
        Move selector cursor to the left
        """
        print(interface_state.select_cursor)
        if interface_state.select_cursor > 0:
            interface_state.select_cursor -= 1

# def tick(dt):
#     pass
#
# pyglet.clock.schedule_interval(tick, 1/60)

pyglet.app.run()
