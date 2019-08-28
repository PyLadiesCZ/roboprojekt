"""
This file is called by Pytest test_loading.py
It checks that the maps have correct structure
Don't call it separately
"""

from loading import get_board


def get_order_tiles(text):
    order_tiles = {
        'Tile': "A_ground",
        'StartTile': "B_start_tile",
        'HoleTile': "C_hole",
        'RepairTile': "C_repair",
        'BeltTile': "C_belt",
        'GearTile': "C_gear",
        'FlagTile': "D_flag",
        'PusherTile': "E_pusher",
        'LaserTile': "E_laser",
        'WallTile': "E_wall",
        'StopTile': "E_stop_tile",
        }
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

            # Tiles with the same type and direction mustn't be in list of types
            if (type(tile).__name__, tile.direction) in tile_type_and_direction:
                print(f"""On coordinates: {coordinate} \
                      there is this tile twice: {type(tile).__name__}. \
                      The tiles mustn't repeat.""")
                return coordinate, type(tile).__name__ # (8, 9), 'wall'
            else:
                tile_type_and_direction.append((type(tile).__name__, tile.direction))

        a = 0
        b = 0
        c = 0
        d = 0

        for letter in tile_type_letter:
            if letter[0] == 'A':
                a += 1
            if letter[0] == 'B':
                b += 1
            if letter[0] == 'C':
                c += 1
            if letter[0] == 'D':
                d += 1
        if a > 1 or b > 1 or c > 1 or d > 1:
            print(f"""On coordinates: {coordinate} \
                  there is this count of layers: a-{a}, b-{b}, c-{c}, d-{d}. \
                  Each layer must be once only.""")
            return coordinate, a, b, c, d  # ((1, 9), 1, 2, 0, 0)

        # Tiles types must be in the correct order.
        # ["A","B","D"] is correct ["D", "A"] is not
        # A < B < C < D
        letters_count = len(tile_type_letter)
        for i in range(letters_count-1):
            if tile_type_letter[i][0] > tile_type_letter[i+1][0]:
                print(f"""On coordinates: {coordinate} \
                      there is wrong layers order: {tile_type_letter[i]}.""")
                return coordinate, tile_type_letter[i]  # ((7, 9), 'D')

        # "Flag" mustn't be over the "Hole" or "Starting tile"
        for i in range(len(tile_type_letter)-1):
            if (tile_type_letter[i] == "C_hole" and tile_type_letter[i+1] == "D_flag") \
            or (tile_type_letter[i] == "B_start_tile" and tile_type_letter[i+1] == "D_flag"):
                print(f"""On coordinates: {coordinate} \
                      there is flag over hole or start: {tile_type_letter[i]}.""")
                return coordinate, tile_type_letter[i]

    return True
