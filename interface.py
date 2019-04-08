from random import shuffle

from backend import Robot, MovementCard, RotationCard
from util import Direction, Rotation


robot_data = Robot(Direction.N, None, "mintbot") # a makeshift fictitious robot
MAX_CARD_COUNT = 9


class InterfaceState:
    def __init__(self, dealt_cards, robot_data):
        self.dealt_cards = dealt_cards
        self.robot_data = robot_data
        self.my_program = [None, None, None, None, None]
        self.power_down = False
        self.indicator = False
        self.cursor_index = 0 # 0-4 number of positon

    def __repr__(self):
        return "<InterfaceState Cards: {}, My Cards: {}, Power Down: {}, Robot: {}>".format(self.dealt_cards, self.my_program, self.power_down, self.robot_data)

    def select_card(self, dealt_card_index):
        """
        Select a card from the dealt cards and put on
        a place where selector is (in the robot program)
        and selector cursor moves to the next free place.
        """
        if self.indicator == False:
            if dealt_card_index >= len(self.dealt_cards):
                return
            if self.dealt_cards[dealt_card_index] not in self.my_program:
                self.my_program[self.cursor_index] = dealt_cards[dealt_card_index]
                self.cursor_index_plus() # After select a card Move with cursor to right


    def return_card(self):
        """
        Return one selected card from your program back to the dealt cards.
        """
        if self.indicator == False:
            self.my_program[self.cursor_index] = None


    def return_cards(self):
        """
        Retrun all cards of your program back to the dealt cards.
        """
        if self.indicator == False:
            self.my_program = [None, None, None, None, None]
            self.cursor_index = 0


    def cursor_index_plus(self):
        """
        Change selecting cursor position to the next one.
        """
        if self.indicator == False:
            if self.cursor_index < 4:
                self.cursor_index += 1


    def cursor_index_minus(self):
        """
        Change selecting cursor position to the previous one.
        """
        if self.indicator == False:
            if self.cursor_index > 0:
                self.cursor_index -= 1


    def switch_power_down(self):
        """
        Switch power down status between True and False.
        When it is True the Robot doesn't play this round.
        """
        if self.indicator == False:
            if self.power_down == False:
                self.power_down = True
            else:
                self.power_down = False


    def confirm_selection(self):
        """
        When indicator is False the player can choose cards and switch Power Down
        When is True the player ended the selection of cards
        """
        self.indicator = True


def create_card_pack():
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
            card_pack.append(MovementCard(first_number + i*5, movement)) # [MovementCard(690, -1)...][]

    for rotation, cards_count, first_number in rotation_cards:
        for i in range(cards_count):
            card_pack.append(RotationCard(first_number + i*5, rotation)) # [RotationCard(865, Rotation.LEFT)....]
    shuffle(card_pack)
    print(card_pack)
    return card_pack


card_pack = create_card_pack()


def get_dealt_cards(card_pack):
    # maximum number of cards is 9
    # robot's damages reduces the count dealt cards
    dealt_cards_count = MAX_CARD_COUNT-robot_data.damages
    dealt_cards = card_pack[-dealt_cards_count:]
    del card_pack[-dealt_cards_count:]
    return dealt_cards


dealt_cards = get_dealt_cards(card_pack)


def get_interface_state():
    interface_state = InterfaceState(dealt_cards, robot_data)
    return interface_state
