"""
This file is called by Pytest test_loading.py
It checks that the maps have correct structure
Don't call it separately
"""

from loading import get_board
from util import Direction


def get_order_tiles(text):
    order_tiles = {
        'Tile': "A_ground",
        'StartTile': "B_start_tile",
        'HoleTile': "B_hole",
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
            print(tile_type_and_direction)
            tile_type_letter.append(get_order_tiles(type(tile).__name__))

            # Tiles with the same type and direction mustn't be in list of types
            if (type(tile).__name__, tile.direction) in tile_type_and_direction:
                print(f"""On coordinates: {coordinate} \
                      there is this tile twice: {type(tile).__name__}. \
                      The tiles mustn't repeat.""")
                return coordinate, type(tile).__name__  # (8, 9), 'wall'
            else:
                tile_type_and_direction.append((type(tile).__name__, tile.direction))

        a = 0
        b = 0
        c = 0
        d = 0
        laser_count = 0

        for letter in tile_type_letter:
            if letter[0] == 'A':
                a += 1
            if letter[0] == 'B':
                b += 1
            if letter[0] == 'C':
                c += 1
            if letter[0] == 'D':
                d += 1
            if letter == "E_laser":
                laser_count += 1
        if a > 1 or b > 1 or c > 1 or d > 1:
            print(f"""On coordinates: {coordinate} \
                  there is this count of tiles: a-{a}, b-{b}, c-{c}, d-{d}. \
                  There must be only one of tile from those types.""")
            return coordinate, a, b, c, d  # ((1, 9), 1, 2, 0, 0)

        # Tiles types must be in the correct order.
        # ["A","B","D"] is correct ["D", "A"] is not
        # A < B < C < D < E
        letters_count = len(tile_type_letter)
        print(tile_type_letter)
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

        # Lasers cannot be in opposite direction: they would cover each other
        # visually and give 2 x damages to robots.
        if laser_count > 1:
            N_or_S = False
            W_or_E = False
            for tile in tile_type_and_direction:
                if tile[0] == "LaserTile":
                    if (tile[1] == Direction.N or tile[1] == Direction.S):
                        if N_or_S:
                            print(f"Lasers in opposite directions on {coordinate}.")
                            return coordinate
                        else:
                            N_or_S = True
                    if (tile[1] == Direction.W or tile[1] == Direction.E):
                        if W_or_E:
                            print(f"Lasers in opposite directions on {coordinate}.")
                            return coordinate
                        else:
                            W_or_E = True

    return True
