from random import shuffle
from backend import Robot, Direction

robot_data = Robot(Direction.N, "./img/robots/png/MintBot_front.png", (4, 4))


class InterfaceState:
    def __init__(self, cards, power_down, robot_data):
        self.cards = cards
        self.power_down = power_down
        self.robot_data = robot_data

    def __repr__(self):
        return "<InterfaceState Cards: {}, Power Down: {}, Robot: {}>".format(self.cards, self.power_down, self.robot_data)

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


def deal_cards():
    card_pack = get_card_pack()
    deal_cards_list = {}
    for i in range(9-robot_data.damagecount):
        deal_cards_list[i+1] =  card_pack.pop()
    return deal_cards_list


def get_power_down():
    return False


def get_interface_state():
    cards = deal_cards()
    power_down = get_power_down()
    interface_state = InterfaceState(cards, power_down, robot_data)
    return interface_state
