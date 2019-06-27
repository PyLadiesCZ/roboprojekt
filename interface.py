from random import shuffle

from backend import MovementCard, RotationCard
from util import Rotation

MAX_CARD_COUNT = 9


class InterfaceState:
    def __init__(self):
        self.dealt_cards = []
        self.robot = None
        self.my_program = [None, None, None, None, None]
        self.power_down = False
        self.indicator = False
        self.cursor_index = 0  # 0-4 number of positon
        self.players = []

    def __repr__(self):
        return f"InterfaceState Cards: {self.dealt_cards}, My Cards: {self.my_program}, Power Down: {self.power_down,}, Robot: {self.robot}"

    def as_dict(self):
        """
        Return dictionary about state of client_interface."
        """
        return {"interface_data": {"my program": self.my_program,
                "power down": self.power_down, "indicator": self.indicator}}

    def select_card(self, dealt_card_index):
        """
        Select a card from the dealt cards and put on
        a place where selector is (in the robot program)
        and selector cursor moves to the next free place.
        """
        if not self.indicator:
            if dealt_card_index >= len(self.dealt_cards):
                return
            if dealt_card_index not in self.my_program:
                self.my_program[self.cursor_index] = dealt_card_index
                # After select a card Move with cursor to right
                self.cursor_index_plus()

    def return_card(self):
        """
        Return one selected card from your program back to the dealt cards.
        """
        if not self.indicator:
            self.my_program[self.cursor_index] = None

    def return_cards(self):
        """
        Retrun all cards of your program back to the dealt cards.
        """
        if not self.indicator:
            self.my_program = [None, None, None, None, None]
            self.cursor_index = 0

    def cursor_index_plus(self):
        """
        Change selecting cursor position to the next one.
        """
        if not self.indicator:
            if self.cursor_index < 4:
                self.cursor_index += 1

    def cursor_index_minus(self):
        """
        Change selecting cursor position to the previous one.
        """
        if not self.indicator:
            if self.cursor_index > 0:
                self.cursor_index -= 1

    def switch_power_down(self):
        """
        Switch power down status between True and False.
        When it is True the Robot doesn't play this round.
        """
        if not self.indicator:
            if not self.power_down:
                self.power_down = True
            else:
                self.power_down = False

    def confirm_selection(self):
        """
        When indicator is False the player can choose cards and switch Power Down.
        When is True the player ended the selection of cards.
        """
        self.indicator = True


def create_card_pack():
    """
    Create pack of cards: 42 movement cards and 42 rotation cards
    with different values and priorities.
    Return shuffled card pack.
    """
    movement_cards = [(-1, 6, 250),
                      (1, 18, 300),
                      (2, 12, 400),
                      (3, 6, 500),
                      ]
    rotation_cards = [(Rotation.U_TURN, 6, 50),
                      (Rotation.LEFT, 18, 100),
                      (Rotation.RIGHT, 18, 200),
                      ]
    card_pack = []

    for movement, cards_count, first_number in movement_cards:
        for i in range(cards_count):
            # [MovementCard(690, -1)...][]
            card_pack.append(MovementCard(first_number + i*5, movement))

    for rotation, cards_count, first_number in rotation_cards:
        for i in range(cards_count):
            # [RotationCard(865, Rotation.LEFT)....]
            card_pack.append(RotationCard(first_number + i*5, rotation))
    shuffle(card_pack)
    return card_pack


def get_dealt_cards(card_pack):
    """
    Deal the cards for robot - he gets one card less for every damage he's got.
    Take and return the first cards from the card pack.
    Delete the dealt cards from the card pack.
    """
    # Maximum number of cards is 9.
    # Robot's damages reduce the count of dealt cards - each damage one card.
    dealt_cards_count = MAX_CARD_COUNT-robot.damages
    dealt_cards = card_pack[-dealt_cards_count:]
    del card_pack[-dealt_cards_count:]
    return dealt_cards
