from random import shuffle
from backend import Robot, MovementCard, RotationCard
from util import Direction, Rotation


robot_data = Robot(Direction.N, "./img/robots/png/mintbot.png", "./img/robots/png/mintbot.png", None) # a makeshift fictitious robot
MAX_CARD_COUNT = 9


class InterfaceState:
    def __init__(self, deal_cards, robot_data):
        self.deal_cards = deal_cards
        self.robot_data = robot_data
        self.my_program = [None, None, None, None, None]
        self.power_down = False
        self.indicator = False
        self.cursor_index = 0 # 0-4 number of positon

    def __repr__(self):
        return "<InterfaceState Cards: {}, My Cards: {}, Power Down: {}, Robot: {}>".format(self.deal_cards, self.my_program, self.power_down, self.robot_data)

    def select_card(self, deal_card_index):
        """
        Select a card from the table and put on
        a place where selector is (in your "hand")
        and selector cursor moves to the next free place.
        """
        if deal_card_index >= len(self.deal_cards):
            return
        if self.deal_cards[deal_card_index] not in self.my_program:
            self.my_program[self.cursor_index] = deal_cards[deal_card_index]
            self.cursor_index_plus() # After select a card Move with cursor to right

    # Return one card back on the teble
    def return_card(self):
        """
        Return one selected card from your program back to the table.
        """
        if self.indicator == False:
            self.my_program[self.cursor_index] = None

    # Return all cards back on the table
    def return_cards(self):
        """
        Retrun all cards of your program back to the table.
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
        When indicator is False the player can choose cards and switch PD
        When is Truh the player ended the selection of cards
        """
        self.indicator = True

# cards_count, first_number, last_number
def create_card_pack():
    cards_move = {'back_up': [-1, 6, 250, 299],
                    'move1': [1, 18, 300, 399],
                    'move2': [2, 12, 400, 499],
                    'move3': [3, 6, 500, 599],
                    }
    cards_rotation = {'u_turn': [Rotation.U_TURN, 6, 50, 99],
                    'left': [Rotation.LEFT, 18, 100, 199],
                    'right': [Rotation.RIGHT, 18, 200, 299],
                    }
    card_pack = []

    for name, number in cards_move.items():
        for i in range(number[1]):
            for i in range(number[2], number[3], 5):
                card_pack.append(MovementCard(i, number[0])) # [MovementCard(690, -1)...][]
    for name, number in cards_rotation.items():
        for i in range(number[1]):
            for i in range(number[2], number[3], 5):
                card_pack.append(RotationCard(i, number[0])) # [RotationCard(865, Rotation.LEFT)....]
    shuffle(card_pack)

    return card_pack


card_pack = create_card_pack()

def get_deal_cards(card_pack):
    deal_cards = []
    # maximum number of cards is 9
    # demagecount reduces the number of cards
    for i in range(MAX_CARD_COUNT-robot_data.damages):
        deal_cards.append((card_pack.pop()))
    return deal_cards


deal_cards = get_deal_cards(card_pack)

def get_interface_state():
    interface_state = InterfaceState(deal_cards, robot_data)
    return interface_state
