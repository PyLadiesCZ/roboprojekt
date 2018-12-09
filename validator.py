from backend import get_board, get_data


def get_order_squares(text):
    order_squares = {
    'ground':"A",
    'hole':"B",
    'starting_square':"B",
    'repair':"B",
    'belt':"B",
    'gear':"B",
    'flag':"C",
    'pusher':"D",
    'laser':"D",
    'wall':"D"}
    return order_squares.get(text)

def img_list(map_name):
    data = get_data("maps/" + map_name + ".json")
    board = get_board(data)

    for type in board.values():
        square_type_letter = []
        for i in type:
            square_type.append(get_order_squares(i.type))

        a = 0
        b = 0
        c = 0
        for letter in square_type_letter:
            if letter == 'A':
                a += 1
            if letter == 'B':
                b += 1
            if letter == 'C':
                c += 1
        if a > 1 or b > 1 or c > 1:
            return False

    if len(square_type) < 6:
        for i in range(b, 6):
            square_type.append('Z')
        print(a)
    for i in range(6):
        if square_type[i]<= square_type[i+1]:
            return True
    else:
        return square_type
