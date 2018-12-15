from random import shuffle
from backend import Robot, Direction

robot_data = Robot(Direction.N, "./img/robots/png/MintBot_front.png", (4, 4))


class InterfaceState:
    def __init__(self, deal_cards, robot_data):
        self.deal_cards = deal_cards
        self.robot_data = robot_data
        self.my_cards = []
        self.power_down = False
        self.select_cursor = 0

    def __repr__(self):
        return "<InterfaceState Cards: {}, My Cards: {}, Power Down: {}, Robot: {}>".format(self.deal_cards, self.my_card, self.power_down, self.robot_data)

# cartds_count, first_number, last_number
def get_card_pack():
    cards_types = {'u_turn': [6, 50, 56],
                'back_up': [5, 250, 255],
                'left': [18, 100, 118],
                'right': [18, 200, 218],
                'move1': [17, 300, 317],
                'move2': [12, 400, 412],
                'move3': [6, 500, 506]
                }
    card_pack = []
    for name, number in cards_types.items():
        for i in range(number[1],number[2]):
            card_pack.append((name, i))
    shuffle(card_pack)
    return(card_pack)


def get_deal_cards():
    card_pack = get_card_pack()
    deal_cards_list = []
    for i in range(9-robot_data.damagecount):
        deal_cards_list.append((card_pack.pop()))
    return deal_cards_list


def get_interface_state():
    deal_cards = get_deal_cards()
    interface_state = InterfaceState(deal_cards, robot_data)
    return interface_state
