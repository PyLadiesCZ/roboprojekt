"""
This file is called by Pytest test_backend.py
It checks that the maps have correct structure
Don't call it separately
"""

from loading import get_board, get_data


def get_order_squares(text):
    order_squares = {
    'ground':"A_ground",
    'hole':"B_hole",
    'starting_square':"B_starting_square",
    'repair':"B_repair",
    'belt':"B_belt",
    'gear':"B_gear",
    'flag':"C_flag",
    'pusher':"D_pusher",
    'laser':"D_laser",
    'wall':"D_wall"}
    return order_squares[text]

def check_squares(map_name):
    """
    Change the list of types squares to the letters.
    A, B and C type can be only once in type list.
    """
    board = get_board(map_name)

    for coordinate, type in board.items():
        square_type_letter = []
        square_type_and_direction = []
        for i in type:
            square_type_letter.append(get_order_squares(i.type))

            """
            Squares with the same type and direction mustn't be in list of types
            """
            if (i.type, i.direction) in square_type_and_direction:
                return coordinate, i.type # (8, 9), 'wall'
            else:
                square_type_and_direction.append((i.type, i.direction))

        a = 0
        b = 0
        c = 0

        for letter in square_type_letter:
            if letter[0] == 'A':
                a += 1
            if letter[0] == 'B':
                b += 1
            if letter[0] == 'C':
                c += 1
        if a > 1 or b > 1 or c > 1:
            return coordinate, a, b, c # ((1, 9), 1, 2, 0)

        """
        Squares types must be in the correct order.
        ["A","B","D"] is correct ["D", "A"] is not
        A < B < C < D
        """
        letters_count = len(square_type_letter)
        for i in range(letters_count-1):
            if square_type_letter[i][0] > square_type_letter[i+1][0]:
                return coordinate, square_type_letter[i] # ((7, 9), 'D')

        """
        "Flag" mustn't be over the "Hole" or "Starting square"
        """
        for i in range(len(square_type_letter)-1):
            if square_type_letter[i] == "B_hole" and  square_type_letter[i+1] == "C_flag" or square_type_letter[i] == "B_starting_square" and  square_type_letter[i+1] == "C_flag":
                return coordinate, square_type_letter[i]


    return True
