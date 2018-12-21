from random import shuffle
from backend import Robot
from util import Direction
robot_data = Robot(Direction.N, "./img/robots/png/mintbot.png", "./img/robots/png/mintbot.png", None)


class InterfaceState:
    def __init__(self, deal_cards, robot_data):
        self.deal_cards = deal_cards
        self.robot_data = robot_data
        self.my_cards = []
        self.power_down = False
        self.cursor_index = 0 # 0-4

    def __repr__(self):
        return "<InterfaceState Cards: {}, My Cards: {}, Power Down: {}, Robot: {}>".format(self.deal_cards, self.my_cards, self.power_down, self.robot_data)

# cards_count, first_number, last_number
def get_card_pack():
    cards_types = {'u_turn': [6, 50, 99],
                'back_up': [5, 250, 299],
                'left': [18, 100, 199],
                'right': [18, 200, 299],
                'move1': [17, 300, 399],
                'move2': [12, 400, 499],
                'move3': [6, 500, 599]
                }
    card_pack = []
    for name, number in cards_types.items():
        for i in range(number[1],number[2],5):
            card_pack.append((name, i))
    shuffle(card_pack)
    return(card_pack)


def get_deal_cards():
    card_pack = get_card_pack()
    deal_cards_list = []
    # maximum number of cards is 9
    # demagecount reduces the number of cards
    for i in range(9-robot_data.damagecount):
        deal_cards_list.append((card_pack.pop()))
    return deal_cards_list


def get_interface_state():
    deal_cards = get_deal_cards()
    interface_state = InterfaceState(deal_cards, robot_data)
    return interface_state
