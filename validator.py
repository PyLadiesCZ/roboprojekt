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
    return order_squares[text]

def img_list(map_name):
    data = get_data("maps/" + map_name + ".json")
    board = get_board(data)

    for coordinate, type in board.items():
        square_type_letter = []
        for i in type:
            square_type_letter.append(get_order_squares(i.type))

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
            return coordinate, a, b, c
        letter_count = len(square_type_letter)
        print(coordinate)
        for i in range(letter_count-1):

            if square_type_letter[i] > square_type_letter[i+1]:
                return coordinate, square_type_letter[i]
    return True
