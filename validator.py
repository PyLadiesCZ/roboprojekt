"""
This file is called by Pytest test_backend.py
It checks that the maps have correct structure
Don't call it separately
"""

from loading import get_board


def get_order_tiles(text):
    order_tiles = {
        'Tile': "A_ground",
        'HoleTile': "B_hole",
        'StartTile': "B_start_tile",
        'RepairTile': "B_repair",
        'BeltTile': "B_belt",
        'GearTile': "B_gear",
        'FlagTile': "C_flag",
        'PusherTile': "D_pusher",
        'LaserTile': "D_laser",
        'WallTile': "D_wall"}
    return order_tiles[text]


def check_tiles(map_name):
    """
    Change the list of tile subclasses to the letters.
    A, B and C type can be only once in type list.
    """
    board = get_board(map_name)

    for coordinate, tiles in board.items():
        tile_type_letter = []
        tile_type_and_direction = []
        for tile in tiles:
            tile_type_letter.append(get_order_tiles(type(tile).__name__))

            """
            Tiles with the same type and direction mustn't be in list of types
            """
            if (type(tile).__name__, tile.direction) in tile_type_and_direction:
                return coordinate, type(tile).__name__ # (8, 9), 'wall'
            else:
                tile_type_and_direction.append((type(tile).__name__, tile.direction))

        a = 0
        b = 0
        c = 0

        for letter in tile_type_letter:
            if letter[0] == 'A':
                a += 1
            if letter[0] == 'B':
                b += 1
            if letter[0] == 'C':
                c += 1
        if a > 1 or b > 1 or c > 1:
            return coordinate, a, b, c  # ((1, 9), 1, 2, 0)

        """
        Tiles types must be in the correct order.
        ["A","B","D"] is correct ["D", "A"] is not
        A < B < C < D
        """
        letters_count = len(tile_type_letter)
        for i in range(letters_count-1):
            if tile_type_letter[i][0] > tile_type_letter[i+1][0]:
                return coordinate, tile_type_letter[i]  # ((7, 9), 'D')

        """
        "Flag" mustn't be over the "Hole" or "Starting tile"
        """
        for i in range(len(tile_type_letter)-1):
            if tile_type_letter[i] == "B_hole" and tile_type_letter[i+1] == "C_flag" or tile_type_letter[i] == "B_start_tile" and tile_type_letter[i+1] == "C_flag":
                return coordinate, tile_type_letter[i]

    return True
