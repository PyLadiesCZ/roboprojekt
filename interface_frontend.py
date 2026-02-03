import pyglet
pyglet.options['shadow_window'] = False

from pyglet.gl import Config as GLConfig
from time import monotonic

from util_frontend import TILE_WIDTH, TILE_HEIGHT, get_label, get_sprite
from util_frontend import (window_zoom, loaded_robots_images, player_sprite_proxy,
                           _init_module_after_gl_context as _util_frontend_init_module_after_gl_context)

MAX_LIVES_COUNT = 3
MAX_FLAGS_COUNT = 8
MAX_DAMAGES_COUNT = 9
WINDOW_WIDTH = 768
WINDOW_HEIGHT = 1024
# Gap between other robots pictures
GAP = 87


def create_window(on_draw, on_text, on_mouse_press, on_close):
    """
    Return a pyglet window for graphic output.
    """
    gl_config = GLConfig(major_version=2, minor_version=1, forward_compatible=False)
    window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT,
                                  config=gl_config, resizable=True)

    _util_frontend_init_module_after_gl_context()
    _init_module_after_gl_context()

    window.push_handlers(
        on_draw=on_draw,
        on_text=on_text,
        on_mouse_press=on_mouse_press,
        on_close=on_close,
    )
    return window

_init_module_after_gl_context_called = False

def _init_module_after_gl_context():
    global interface_sprite, power_down_sprite, power_down_player_sprite
    global crown_sprite, loss_sprite, indicator_green_sprite, indicator_red_sprite
    global card_background_sprite, own_border_sprite, select_sprite
    global cursor_sprite, you_win_sprite, winner_of_the_game_sprite
    global game_over_sprite, players_background, my_robot_sprite, flag_slot_sprite
    global _init_module_after_gl_context_called
    if _init_module_after_gl_context_called:
        return
    _init_module_after_gl_context_called = True

    # Interface element sprites
    # Interface background
    interface_sprite = get_sprite('img/interface/png/interface.png', x=0, y=0)
    power_down_sprite = get_sprite('img/interface/png/power.png', x=210, y=900)
    power_down_player_sprite = get_sprite('img/interface/png/power_player.png')
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
    # Own robot's border
    own_border_sprite = get_sprite('img/interface/png/own_border.png', x=33, y=42)
    # Gray overlay on selected cards
    select_sprite = get_sprite('img/interface/png/card_cv.png')
    # Selection cursor
    cursor_sprite = get_sprite('img/interface/png/card_sl.png')
    # Winner
    you_win_sprite = get_sprite('img/interface/png/winner.png', x=160, y=290)
    winner_of_the_game_sprite = get_sprite('img/interface/png/game_winner.png', x=160, y=200)
    # Game over
    game_over_sprite = get_sprite('img/interface/png/game_over.png', x=140, y=280)
    # Other robot card
    players_background = get_sprite('img/interface/png/player.png')
    # My_robot_sprite, below replaced with the actual image.
    my_robot_sprite = get_sprite('img/robots/png/bender.png', x=64, y=882)
    flag_slot_sprite = get_sprite('img/interface/png/flag_slot.png')

    for i in range(MAX_LIVES_COUNT):
        x = 354 + i * 46
        y = 864
        lives_sprites.append(get_sprite('img/interface/png/life.png', x, y))
    for i in range(MAX_FLAGS_COUNT):
        x = 332 + i * 48
        y = 928
        flags_sprites.append(get_sprite(f'img/tiles/png/flag_{i+1}.png', x, y))

    for i in range(MAX_DAMAGES_COUNT):
        x = 677 + i * -70
        y = 773
        damages_tokens_sprites.append(get_sprite('img/interface/png/token.png', x, y))

    for i in range(MAX_DAMAGES_COUNT):
        x = 677 + i * -70
        y = 773
        permanent_damages_sprites.append(get_sprite('img/interface/png/permanent_damage.png', x, y))

    cards_type_sprites.update({
        'u_turn': get_sprite('img/interface/png/u_turn.png'),
        'back_up': get_sprite('img/interface/png/back.png'),
        'left': get_sprite('img/interface/png/rotate_left.png'),
        'right': get_sprite('img/interface/png/rotate_right.png'),
        'move1': get_sprite('img/interface/png/move1.png'),
        'move2': get_sprite('img/interface/png/move2.png'),
        'move3': get_sprite('img/interface/png/move3.png'),
    })

    for i in range(5):
        x, y = 47, 384
        # 144 space between cards
        x = x + i * 144
        dealt_cards_coordinates.append((x, y))
    for i in range(4):
        x, y = 120, 224
        x = x + i * 144
        dealt_cards_coordinates.append((x, y))
    for i in range(5):
        x, y = 47, 576
        x = x + i * 144
        program_coordinates.append((x, y))

lives_sprites = []
flags_sprites = []

# Tokens of damage
damages_tokens_sprites = []

permanent_damages_sprites = []

# Cards sprites
cards_type_sprites = {}

dealt_cards_coordinates = []

program_coordinates = []

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
    priority_label = get_label(
        str(card.priority),
        x=x_priority,
        y=y_priority,
        font_size=14,
        anchor_x="right",
        color=(255, 255, 255, 255),
    )
    priority_label.draw()

    # Draw card name
    x_name = x + 50
    y_name = y + 20
    card_name = cards_type_names[card.name]

    name_label = get_label(
        card_name,
        x=x_name,
        y=y_name,
        font_size=10,
        anchor_x="center",
        color=(255, 255, 255, 255),
    )
    name_label.draw()


def draw_interface(interface_state, game_state, winner_time, window):
    """
    Draw the images of given interface,
    react to user's resizing of window by scaling the interface.
    """
    with window_zoom(window, WINDOW_WIDTH, WINDOW_HEIGHT):
        # Interface background
        interface_sprite.draw()

        # CARDS
        # Dealt cards
        for coordinate, card in zip(
                dealt_cards_coordinates,
                interface_state.dealt_cards,
                ):
            draw_card(coordinate, card)

        if game_state is not None:
            players = []
            for robot in game_state.robots:
                if interface_state.robot and interface_state.robot.name != robot.name:
                    players.append(robot)

            # Other robots and their attributes
            for i, robot in enumerate(players):
                draw_robot(i, robot, game_state)

            # Flag slot
            for i in range(game_state.flag_count):
                flag_slot_sprite.x = 332 + i * 48
                flag_slot_sprite.y = 928
                flag_slot_sprite.draw()

            # Game over
            if interface_state.robot is None:
                game_over_sprite.draw()

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
        if interface_state.timer is not None:
            seconds = monotonic() - interface_state.timer
            seconds_left = round(30-seconds)
            timer_label = get_label(
                # format'02' means that number has always 2 digits,
                # shorter is filled with '0' before it.
                f"00:{seconds_left:02}",
                x=585,
                y=865,
                font_size=26,
                anchor_x="center",
                color=(255, 0, 0, 255),
            )
            timer_label.draw()

        # Indicator
        if not interface_state.selection_confirmed:
            indicator_green_sprite.draw()
        else:
            indicator_red_sprite.draw()

        if interface_state.robot:
            # Robot
            my_robot_sprite.image = loaded_robots_images[interface_state.robot.name]
            my_robot_sprite.draw()
            draw_robot(-1, interface_state.robot, game_state)
            own_border_sprite.draw()

            robot_name = get_label(
                interface_state.robot.displayed_name,
                x=248,
                y=864,
                font_size=16,
                anchor_x="center",
                color=(0, 0, 0, 255),
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

            # Winner
            if game_state.winners:
                # An announcement of winner is drawn for 5 sec from time,
                # when client received message about winner.
                # Winner crown is drawn for the rest of the game.
                if interface_state.robot.winner:
                    crown = crown_sprite
                else:
                    crown = loss_sprite
                crown.x = 116
                crown.y = 938
                crown.draw()

                seconds = 5 - (monotonic() - winner_time)
                if (0 < seconds < 5):
                    if interface_state.robot.winner:
                        announcement = you_win_sprite
                        announcement.draw()
                    else:
                        announcement = winner_of_the_game_sprite
                        announcement.draw()
                        for i, name in enumerate(game_state.winners):
                            winner_label = get_label(
                                str(name),
                                x=(game_state.tile_count[0] * TILE_WIDTH) / 2 - 50,
                                y=(game_state.tile_count[1] * TILE_HEIGHT) / 2 - 100 - i * 50,
                                font_size=26,
                                anchor_x="center",
                                color=(255, 0, 0, 255),
                            )
                            winner_label.draw()


def draw_robot(i, robot, game_state):
    """
    Draw robot and his attributes.
    """
    # Robot's background
    players_background.x = 120 + i * GAP
    players_background.y = 40
    players_background.draw()

    # Robot´s image
    if robot.name in loaded_robots_images:
        player_sprite_proxy.image = loaded_robots_images[robot.name]
        player_sprite_proxy.x = 139 + i * GAP
        player_sprite_proxy.y = 90
        player_sprite_proxy.draw()

    # Robot's name
    robot_name_label = get_label(
        str(robot.displayed_name),
        x=170 + GAP * i,
        y=75,
        font_size=10,
        anchor_x="center",
        color=(0, 0, 0, 255),
    )
    robot_name_label.draw()

    # Power_down
    if robot.power_down:
        power_down_player_sprite.x = 153 + GAP * i
        power_down_player_sprite.y = 95
        power_down_player_sprite.draw()

    # Robot´flags
    flag_label = get_label(
        str(robot.flags),
        x=205 + GAP * i,
        y=160,
        font_size=16,
        anchor_x="right",
        color=(0, 0, 0, 255),
    )
    flag_label.draw()

    # Robot´damages
    damage_label = get_label(
        str(robot.damages),
        x=165 + GAP * i,
        y=54,
        font_size=16,
        anchor_x="right",
        color=(0, 0, 0, 255),
    )
    damage_label.draw()

    permanent_damage_label = get_label(
        str(robot.permanent_damages),
        x=205 + GAP * i,
        y=54,
        font_size=16,
        anchor_x="right",
        color=(0, 0, 0, 255),
    )
    permanent_damage_label.draw()

    # Robot´lives
    life_label = get_label(
        str(robot.lives),
        x=165 + GAP * i,
        y=160,
        font_size=16,
        anchor_x="right",
        color=(0, 0, 0, 255),
    )
    life_label.draw()

    # Winner crown
    if game_state.winners:
        if robot.winner:
            sprite = crown_sprite
        else:
            sprite = loss_sprite

        sprite.x = 133 + i * GAP
        sprite.y = 80
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

    # Switch on and off Power Down token
    if text == 'p':
        interface_state.switch_power_down()

    # Confirm selection of cards
    if text == 'k':
        interface_state.confirm_selection()


def handle_click(interface_state, x, y, window):
    """
    Interface reacts on mouse press.
    """
    # Transform x, y coordinates according to zoom of window.
    zoom = min(
        window.height / WINDOW_HEIGHT,
        window.width / WINDOW_WIDTH
    )
    x, y = (x / zoom, y / zoom)
    # Select a card and take it in your "hand"
    # Selected card is in "GREEN" cursor
    card_sprite = cards_type_sprites["u_turn"]
    for i, coordinate in enumerate(dealt_cards_coordinates):
        coord_x, coord_y = coordinate
        if coordinates_in_rectangle(
            x, y, coord_x, coord_y, card_sprite.width, card_sprite.height
        ):
            interface_state.select_card(i)

    # Confirm selection of cards
    if coordinates_in_rectangle(
        x, y, indicator_red_sprite.x, indicator_red_sprite.y,
        indicator_red_sprite.width, indicator_red_sprite.height
    ):
        interface_state.confirm_selection()

    # Switch on and off Power Down token
    if coordinates_in_rectangle(
        x, y, power_down_sprite.x, power_down_sprite.y,
        power_down_sprite.width, power_down_sprite.height
    ):
        interface_state.switch_power_down()

    # Cursor
    for i, coordinate in enumerate(program_coordinates):
        coord_x, coord_y = coordinate
        if coordinates_in_rectangle(
            x, y, coord_x, coord_y, card_sprite.width, card_sprite.height
        ):
            if i < len(interface_state.program):
                interface_state.cursor_index = i

    # Return all cards
    # The numbers are coordinate of "Return all cards" rectangle
    if (445 < x < 635) and (535 < y < 565):
        interface_state.return_cards()

    # Return card
    # The numbers are coordinate of "Return one card" rectangle
    if (250 < x < 435) and (535 < y < 565):
        interface_state.return_card()


def coordinates_in_rectangle(x, y, left, bottom, width, height):
    """
    Return True if coordinates x, y are in the defined rectangle and False if they are out of the rectangle.
    """
    return (left < x < left+width and bottom < y < bottom+height)
