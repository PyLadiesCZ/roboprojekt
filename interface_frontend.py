import pyglet

from interface import get_interface_state


interface_state = get_interface_state()
MAX_CARDS_COUNT = 9
MAX_LIVES_COUNT = 3
MAX_FLAGS_COUNT = 8
MAX_DAMAGES_COUNT = 9


def create_window():
    """
    Return a pyglet window for graphic output.
    """
    window = pyglet.window.Window(768, 1024, resizable=True)
    return window
window = create_window()


def get_sprite(img_path, x=0, y=0):
    img = pyglet.image.load(img_path)
    return pyglet.sprite.Sprite(img, x, y)


# Interface element sprites
interface_sprite = get_sprite('img/interface/png/interface.png', x=0, y=0) # All Interface background
power_down_sprite = get_sprite('img/interface/png/power.png', x=186, y=854)
indicator_green_sprite = get_sprite('img/interface/png/green.png',  x=688, y=864) # Time indicator
indicator_red_sprite = get_sprite('img/interface/png/red.png',  x=688, y=864) # Time indicator
card_background_sprite = get_sprite('img/interface/png/card_bg.png') # Universal cards background
select_sprite = get_sprite('img/interface/png/card_cv.png') # Gray overlay on selected cards
cursor_sprite = get_sprite('img/interface/png/card_sl.png') # Selection cursor
my_robot_sprite = get_sprite(interface_state.robot_data.path, x=74, y=888) # My Robot img

lives_sprite = []
for i in range(MAX_LIVES_COUNT):
    x = 354 + i * 46
    y = 864
    lives_sprite.append(get_sprite('img/interface/png/life.png', x, y))

flags_sprite = []
for i in range(MAX_FLAGS_COUNT):
    x = 332 + i * 48
    y = 928
    flags_sprite.append(get_sprite('img/tiles/png/flag_{}.png'.format(i+1), x, y))

damages_tokens_sprite = [] # Tokens of damage
for i in range(MAX_DAMAGES_COUNT):
    x = 676 + i * -70
    y = 768
    damages_tokens_sprite.append(get_sprite('img/interface/png/token.png', x, y))

# Cards Sprites
cards_type_sprites = {
    'u_turn': get_sprite('img/interface/png/u_turn.png'),
    'back_up': get_sprite('img/interface/png/back.png'),
    'left': get_sprite('img/interface/png/rotate_left.png'),
    'right': get_sprite('img/interface/png/rotate_right.png'),
    'move1': get_sprite('img/interface/png/move1.png'),
    'move2': get_sprite('img/interface/png/move2.png'),
    'move3': get_sprite('img/interface/png/move3.png'),
}

dealt_cards_coordinates = []
for i in range(5):
    x, y = 47, 384
    x = x + i * 144 # 144 space between cards
    dealt_cards_coordinates.append((x, y))
for i in range(4):
    x, y = 120, 224
    x = x + i * 144
    dealt_cards_coordinates.append((x, y))

program_coordinates = []
for i in range(5):
    x, y = 47, 576
    x = x + i * 144
    program_coordinates.append((x, y))

# dict for drawing cards names
cards_type_names = {
    'u_turn': 'U TURN',
    'back_up': 'BACK UP',
    'left': 'LEFT',
    'right': 'RIGHT',
    'move1': 'MOVE 1',
    'move2': 'MOVE 2',
    'move3': 'MOVE 3',
}

def draw_card(coordinate, card):
    """
    Draw one card
    Take coordinate and type of card and return all image with background,
    number and direction image.
    """
    x, y = coordinate

    # Draw universal background
    card_background_sprite.x = x
    card_background_sprite.y = y
    card_background_sprite.draw()

    # Draw card type
    card_sprite = cards_type_sprites[card.name]
    card_sprite.x = x
    card_sprite.y = y
    card_sprite.draw()

    # Draw card value
    x_priority = x + 70
    y_priority = y + 118
    priority = pyglet.text.Label(text=str(card.priority), font_size=14, x=x_priority, y=y_priority, anchor_x='right')
    priority.draw()

    # Draw card name
    x_name = x + 50
    y_name = y + 20
    card_name = cards_type_names[card.name]
    name = pyglet.text.Label(text=card_name, font_size=10, x=x_name, y=y_name, anchor_x='center')
    name.draw()

def draw_interface(window):
    """
    Draw the images of interface, react to user's resizing of window by scaling the interface.
    """
    pyglet.gl.glPushMatrix()
    window.clear()
    zoom = min(
        window.height / 1024,
        window.width / 768
    )
    pyglet.gl.glScalef(zoom, zoom, 1)

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
    for sprite in damages_tokens_sprite[0:interface_state.robot_data.damages]:
        sprite.draw()

    # CARDS
    # Dealt cards
    for coordinate, card in zip(dealt_cards_coordinates, interface_state.dealt_cards):
        draw_card(coordinate, card) # draw_card(coordinate, card_type)

    # Cards hand
    for coordinate, card in zip(program_coordinates, interface_state.my_program):
        if card != None: # if selected card exist
            draw_card(coordinate, card)

    # Selected cards
    # if card is selected, selected card in dealt cards is gray
    for card in interface_state.my_program:
        if card != None:
            x, y = dealt_cards_coordinates[interface_state.dealt_cards.index(card)]
            select_sprite.x = x
            select_sprite.y = y
            select_sprite.draw()

    # Cursor
    x, y = program_coordinates[interface_state.cursor_index]
    cursor_sprite.x = x
    cursor_sprite.y = y
    cursor_sprite.draw()

    # Power Down
    if interface_state.power_down == True:
        power_down_sprite.draw()

    # Indicator
    if interface_state.indicator == False:
        indicator_green_sprite.draw()
    else:
        indicator_red_sprite.draw()


    pyglet.gl.glPopMatrix()


@window.event
def on_draw():
    window.clear()
    draw_interface(window)


CARD_KEYS= ["q", "w", "e", "r", "t", "a","s", "d", "f"]


@window.event
def on_text(text):
    """
    Key listener
    Wait for user input on keyboard and react for it.
    """
    if text in CARD_KEYS:
        # Select a card and take it in your "hand"
        # Selected card is in "GREEN" cursor
        dealt_card_index = CARD_KEYS.index(text)
        interface_state.select_card(dealt_card_index)

    # Return one card back to the dealt cards
    if text == 'i':
        interface_state.return_card()

    # Return all cards back to the dealt cards
    if text == 'o':
        interface_state.return_cards()

    # Move  selector cursor to the right
    if text == 'm':
        interface_state.cursor_index_plus()

    # Move selector cursor to the left
    if text == 'n':
        interface_state.cursor_index_minus()

    # Put and take a Power Down token
    if text == 'p':
        interface_state.switch_power_down()

    # confirm selection of cards
    if text == 'k':
        interface_state.confirm_selection()

pyglet.app.run()
