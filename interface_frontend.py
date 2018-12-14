import pyglet
from pyglet.window import key
from interface import get_interface_state
from enum import Enum


window = pyglet.window.Window(768, 1024)
interface_state = get_interface_state()

#my cards
cards_3 = [(47, 576), 5, 144]

cards_type_paths = {'u_turn': 'interface/png/u_turn.png',
                    'back_up': 'interface/png/back.png',
                    'left': 'interface/png/rotate_left.png',
                    'right': 'interface/png/rotate_right.png',
                    'move1': 'interface/png/move.png',
                    'move2': 'interface/png/move.png',
                    'move3': 'interface/png/move.png'}


class InterfaceData(Enum):
    interface =(0, 0),1, 0,'interface/png/interface.png'
    lives = (354, 864), 3, 46, 'interface/png/life.png'
    indicator = (688, 864), 1, 0, 'interface/png/green.png'
    flags = (332, 928), 8, 48, 'img/squares/png/flag_{}.png'
    tokens = (676, 768), 10, -70, 'interface/png/token.png'
    power_down = (186, 854), 1, 0, 'interface/png/power.png'
    my_robot = (74, 888), 1, 0, interface_state.robot_data.path,

    def __init__(self, first_coordinates, elements_count, space, path):
        self.first_coordinates = first_coordinates
        self.elements_count = elements_count
        self.space = space
        self.path = path


def get_cards_on_table_coordinates():
    cards_row_1 = [(47, 384), 5, 144,]
    cards_row_2 = [(120, 224), 4, 144]
    cards_on_table_coordinates = {}
    for i in range(cards_row_1[1]+1):
        coordinate = {}
        x, y = cards_row_1[0]
        x = x + i* cards_row_1[2]
        cards_on_table_coordinates[(i+1)] = (x, y)
    for i in range(cards_row_2[1]):
        coordinate = {}
        x, y = cards_row_2[0]
        x = x + i* cards_row_2[2]
        cards_on_table_coordinates[(i+6)] = (x, y)
    return cards_on_table_coordinates




def cards_sprites():
    cards_on_table_coordinates = get_cards_on_table_coordinates()
    sprites = []

    for number, type in interface_state.cards.items():
        x, y = cards_on_table_coordinates[number]
        name, value = type
        path = cards_type_paths[name]
        """
        Add a universal card background
        """
        background =  'interface/png/card_bg.png'
        img = pyglet.image.load(background)
        sprite = pyglet.sprite.Sprite(img, x, y)
        sprites.append(sprite)
        """
        Add a card type symbol
        """
        type = pyglet.image.load(path)
        sprite = pyglet.sprite.Sprite(type, x, y)
        sprites.append(sprite)
        """
        Card value (number on the card)
        """
        x = x + 70
        y = y + 118
        text = pyglet.text.Label(text = str(value), font_size = 14, x = x, y = y, anchor_x = 'right')
        sprites.append(text)
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
    draw_interface(create_sprites(InterfaceData.interface))
    draw_interface(create_sprites(InterfaceData.tokens)[0:interface_state.robot_data.injurycount])
    draw_interface(cards_sprites())
    draw_interface(create_sprites(InterfaceData.lives)[0:interface_state.robot_data.lifecount])
    if interface_state.power_down == True:
        draw_interface(create_sprites(InterfaceData.power_down))
    draw_interface(create_sprites(InterfaceData.flags)[0:interface_state.robot_data.flagcount])
    draw_interface(create_sprites(InterfaceData.my_robot))

def create_label():
    return pyglet.text.Label(
                             font_size=18,
                             x=10,
                             y=window.height//2,
                             anchor_x='left',
                             anchor_y='center')


label = create_label()


@window.event
def on_draw():
    window.clear()
    interface()

@window.event
def on_text(text):
    label.text = text
    print(text)
    on_draw()

def tick(dt):
    pass

pyglet.clock.schedule_interval(tick, 1/60)

pyglet.app.run()
