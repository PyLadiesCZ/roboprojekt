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

    for type in board.values():
        square_type_letter = []
        for i in type:
            square_type_letter.append(get_order_squares(i.type)[0])

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
            return square_type_letter
    letter_count = len(square_type_letter)
    if letter_count < 6:
        for i in range(letter_count, 6):
            square_type_letter.append('Z')

    if square_type_letter[0] <= square_type_letter[1] <= square_type_letter[2] <= square_type_letter[3] <= square_type_letter[4] <= square_type_letter[5]:
        return True
    else:
        return square_type_letter
