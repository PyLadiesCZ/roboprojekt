from random import shuffle
from backend import Robot
from util import Direction


robot_data = Robot(Direction.N, "./img/robots/png/mintbot.png", "./img/robots/png/mintbot.png", None) # a makeshift fictitious robot
MAX_CARD_COUNT = 9

class InterfaceState:
    def __init__(self, deal_cards, robot_data):
        self.deal_cards = deal_cards
        self.robot_data = robot_data
        self.my_cards = [None, None, None, None, None]
        self.power_down = False
        self.cursor_index = 0 # 0-4 number of positon

    def __repr__(self):
        return "<InterfaceState Cards: {}, My Cards: {}, Power Down: {}, Robot: {}>".format(self.deal_cards, self.my_cards, self.power_down, self.robot_data)



    def select_card(self, deal_card_index):
        """
        Select a card from the table and put on
        a place where selector is (in your "hand")
        and selector cursor moves to the next free place.
        """
        if deal_card_index >= len(self.deal_cards):
            return
        if self.deal_cards[deal_card_index] not in self.my_cards:
            self.my_cards[self.cursor_index] = deal_cards[deal_card_index]
            self.cursor_index_plus() # After select a card Move with cursor to right


    # Return one card back on the teble
    def return_card(self):
        """
        Return one selected card from your hand back to the table.
        """
        self.my_cards[self.cursor_index] = None


    # Return all cards back on the table
    def return_cards(self):
        """
        Retrun all cards of your hand back to the table.
        """

        self.my_cards = [None, None, None, None, None]
        self.cursor_index = 0


    def cursor_index_plus(self):
        """
        Change selecting cursor position to the next one.
        """
        if self.cursor_index < 4:
            self.cursor_index += 1


    def cursor_index_minus(self):
        """
        Change selecting cursor position to the previous one.
        """
        if self.cursor_index > 0:
            self.cursor_index -= 1


    def switch_power_down(self):
        """
        Switch power down status between True and False.
        When it is True the Robot doesn't play this round.
        """
        if self.power_down == False:
            self.power_down = True
        else:
            self.power_down = False


# cards_count, first_number, last_number
def create_card_pack():
    cards_types = {'u_turn': [6, 50, 99],
                'back_up': [6, 250, 299],
                'left': [18, 100, 199],
                'right': [18, 200, 299],
                'move1': [18, 300, 399],
                'move2': [12, 400, 499],
                'move3': [6, 500, 599],
                }
    card_pack = []
    for name, number in cards_types.items():
        for i in range(number[0]):
            for i in range(number[1], number[2], 5):
                card_pack.append((name, i)) # [('u_turn', 50), ('u_turn', 55)...]
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
