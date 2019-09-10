import pyglet
from pathlib import Path
from functools import lru_cache


MAX_LIVES_COUNT = 3
MAX_FLAGS_COUNT = 8
MAX_DAMAGES_COUNT = 9


def create_window(on_draw, on_text):
    """
    Return a pyglet window for graphic output.
    """
    window = pyglet.window.Window(768, 1024, resizable=True)
    window.push_handlers(
        on_draw=on_draw,
        on_text=on_text,
    )
    return window


def get_sprite(img_path, x=0, y=0):
    img = pyglet.image.load(img_path)
    return pyglet.sprite.Sprite(img, x, y)


# Interface element sprites
# Interface background
interface_sprite = get_sprite('img/interface/png/interface.png', x=0, y=0)
power_down_sprite = get_sprite('img/interface/png/power.png', x=210, y=900)
# Timer
timer_sprite = get_sprite('img/interface/png/timer_on.png', x=521, y=864)
# Winner crown
crown_sprite = get_sprite('img/interface/png/crown.png')
# Loss crown
loss_sprite = get_sprite('img/interface/png/no_crown.png')
# Time indicator
indicator_green_sprite = get_sprite('img/interface/png/green.png', x=688, y=864)
# Time indicator
indicator_red_sprite = get_sprite('img/interface/png/red.png', x=688, y=864)
# Universal cards background
card_background_sprite = get_sprite('img/interface/png/card_bg.png')
# Gray overlay on selected cards
select_sprite = get_sprite('img/interface/png/card_cv.png')
# Selection cursor
cursor_sprite = get_sprite('img/interface/png/card_sl.png')
# Winner
winner_sprite = get_sprite('img/interface/png/winner.png', x=160, y=290)
# Game over
game_over_sprite = get_sprite('img/interface/png/game_over.png', x=140, y=280)
# Other robot card
players_background = get_sprite('img/interface/png/player.png')
# Loading of robots images
loaded_robots_images = {}
for image_path in Path('./img/robots/png').iterdir():
    loaded_robots_images[image_path.stem] = pyglet.image.load(image_path)

# Player_sprite and my_robot_sprite use fake images just to create sprites,
# below replaced with the actual ones.
player_sprite = get_sprite('img/robots/png/bender.png')
my_robot_sprite = get_sprite('img/robots/png/bender.png', x=74, y=888)

lives_sprites = []
for i in range(MAX_LIVES_COUNT):
    x = 354 + i * 46
    y = 864
    lives_sprites.append(get_sprite('img/interface/png/life.png', x, y))

flags_sprites = []
for i in range(MAX_FLAGS_COUNT):
    x = 332 + i * 48
    y = 928
    flags_sprites.append(get_sprite(f'img/tiles/png/flag_{i+1}.png', x, y))

flag_slot_sprite = get_sprite('img/interface/png/flag_slot.png')

# Tokens of damage
damages_tokens_sprites = []
for i in range(MAX_DAMAGES_COUNT):
    x = 676 + i * -70
    y = 768
    damages_tokens_sprites.append(get_sprite('img/interface/png/token.png', x, y))

permanent_damages_sprites = []
for i in range(MAX_DAMAGES_COUNT):
    x = 676 + i * -70
    y = 768
    permanent_damages_sprites.append(get_sprite('img/interface/png/permanent_damage.png', x, y))

# Cards sprites
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
    # 144 space between cards
    x = x + i * 144
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


@lru_cache(maxsize=100)
def get_label(text, x, y, font_size, anchor_x, color):
    """
    Return text label with parameters defined from given arguments.
    Store last 100 labels in cache, documented here:
    https://docs.python.org/3/library/functools.html#functools.lru_cache
    """
    label = pyglet.text.Label()
    label.text = text
    label.x = x
    label.y = y
    label.font_size = font_size
    label.anchor_x = anchor_x
    label.color = color
    return label


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
    priority_label = get_label(
        str(card.priority),
        x_priority,
        y_priority,
        14,
        "right",
        (255, 255, 255, 255)
    )
    priority_label.draw()

    # Draw card name
    x_name = x + 50
    y_name = y + 20
    card_name = cards_type_names[card.name]

    name_label = get_label(
        card_name,
        x_name,
        y_name,
        10,
        "center",
        (255, 255, 255, 255)
    )
    name_label.draw()


def draw_interface(interface_state, window):
    """
    Draw the images of given interface,
    react to user's resizing of window by scaling the interface.
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

    if interface_state.dealt_cards:
        # CARDS
        # Dealt cards
        for coordinate, card in zip(
                dealt_cards_coordinates,
                interface_state.dealt_cards,
                ):
            draw_card(coordinate, card)

    if interface_state.players:
        # Other robots background
        for i in range(len(interface_state.players)):
            players_background.x = 50 + i * 98
            players_background.y = 50
            players_background.draw()

        # Other robots and their attributes
        for i, robot in enumerate(interface_state.players):
            draw_robot(i, robot, interface_state)

    # Cards on hand
    for coordinate, card_index in zip(program_coordinates, interface_state.program):
        if card_index is not None:
            draw_card(coordinate, interface_state.dealt_cards[card_index])

    # Blocked cards
    if interface_state.blocked_cards:
        blocked_cards_coordinates = program_coordinates[-(len(interface_state.blocked_cards)):]

        for coordinate, card in zip(blocked_cards_coordinates, interface_state.blocked_cards):
            draw_card(coordinate, card)

    # Selected cards
    # if card is selected, selected card in dealt cards is gray
    for card_index in interface_state.program:
        if card_index is not None:
            card = interface_state.dealt_cards[card_index]
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
    if interface_state.power_down:
        power_down_sprite.draw()

    # Timer
    if interface_state.timer:
        timer_sprite.draw()

    # Indicator
    if not interface_state.selection_confirmed:
        indicator_green_sprite.draw()
    else:
        indicator_red_sprite.draw()

    # Flag slot
    for i in range(interface_state.flag_count):
        flag_slot_sprite.x = 341 + i * 48
        flag_slot_sprite.y = 933
        flag_slot_sprite.draw()

    if interface_state.robot:
        # Robot
        my_robot_sprite.image = loaded_robots_images[interface_state.robot.name]
        my_robot_sprite.draw()

        robot_name = get_label(
            interface_state.robot.name,
            250, 862, 20,
            "center",
            (0, 0, 0, 255),
        )
        robot_name.draw()

        # Flags
        for sprite in flags_sprites[0:interface_state.robot.flags]:
            sprite.draw()

        # Robot lives
        for sprite in lives_sprites[0:interface_state.robot.lives]:
            sprite.draw()

        # Damage Tokens
        damages = interface_state.robot.damages + interface_state.robot.permanent_damages
        for sprite in damages_tokens_sprites[0:damages]:
            sprite.draw()

        for sprite in permanent_damages_sprites[0:interface_state.robot.permanent_damages]:
            sprite.draw()

        # Winner crown
        if interface_state.winner:
            if interface_state.robot.winner:
                sprite = crown_sprite
            else:
                sprite = loss_sprite

            sprite.x = 120
            sprite.y = 945
            sprite.draw()

    pyglet.gl.glPopMatrix()

def draw_robot(i, robot, interface_state):
    """
    Draw robot and his attributes.
    """
    # Robot´s image
    if robot.name in loaded_robots_images:
        player_sprite.image = loaded_robots_images[robot.name]
        player_sprite.x = 68 + i * 98
        player_sprite.y = 90
        player_sprite.draw()

    # Robot´flags
    flag_label = get_label(
        str(robot.flags),
        132 + 100 * i,
        160,
        20,
        "right",
        (0, 0, 0, 255)
    )
    flag_label.draw()

    # Robot´damages
    damage_label = get_label(
        str(robot.damages),
        92 + 100 * i,
        56,
        20,
        "right",
        (0, 0, 0, 255)
    )
    damage_label.draw()

    permanent_damage_label = get_label(
        str(robot.permanent_damages),
        132 + 100 * i,
        56,
        20,
        "right",
        (0, 0, 0, 255)
    )
    permanent_damage_label.draw()

    # Robot´lives
    life_label = get_label(
        str(robot.lives),
        92 + 100 * i,
        160,
        20,
        "right",
        (0, 0, 0, 255)
    )
    life_label.draw()
    
    # Winner crown
    if interface_state.winner:
        if robot.winner:
            sprite = crown_sprite
        else:
            sprite = loss_sprite

        sprite.x = 78 + i * 98
        sprite.y = 90
        sprite.draw()

CARD_KEYS = ["q", "w", "e", "r", "t", "a", "s", "d", "f"]


def handle_text(interface_state, text):
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

    # Confirm selection of cards
    if text == 'k':
        interface_state.confirm_selection()
