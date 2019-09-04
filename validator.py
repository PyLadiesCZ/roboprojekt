"""
This file is called by Pytest test_loading.py
It checks that the maps have correct structure
Don't call it separately
"""

from loading import get_board
from util import Direction, Rotation


class RepeatingTilesError(Exception):
    """Raised when there are two the same tiles on the same coordinates.
    """


class WrongLayersOrderError(Exception):
    """
    Raised when the layers are in the incorrect order which may lead to
    covering visible elements of the map.
    """


class TilesOfOneTypeError(Exception):
    """
    Raised when there is too many tiles of one type on the same coordinates.
    Eg. Repair or gear tile mustn't repeat, there may be one only.
    """


class FlagOnStartOrHoleError(Exception):
    """Raised when flag covers start or hole tile."""


class LasersInOppositeDirectionError(Exception):
    """
    Raised when lasers are heading opposite directions,
    therefore are not visible.
    """


class LasersWithoutWallError(Exception):
    """Raised when there is no wall at the beginning of the laser."""


class NumberedTilesNotInOrderError(Exception):
    """Raised when numbered tiles like flags or starts are either:
    - not in order (eg. 1, 2, 6, 7)
    - starting from different number than 1 (eg. 0, 1, 2 or 5, 6, 7)
    """


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
    flags = []
    starts = []
    for coordinate, tiles in board.items():
        tile_type_letter = []
        tiles_on_coordinate = []
        for tile in tiles:
            tile_type_letter.append(get_order_tiles(type(tile).__name__))

            """
            Tiles with the same type and direction mustn't be in list of types
            """
            if tile in tiles_on_coordinate:
                print(f"""On coordinates: {coordinate} \
                      there is this tile twice: {tile.name}. \
                      The tiles mustn't repeat.""")
                raise RepeatingTilesError
            else:
                tiles_on_coordinate.append(tile)

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
            raise TilesOfOneTypeError

        """
        Tiles types must be in the correct order.
        ["A","B","D"] is correct ["D", "A"] is not
        A < B < C < D < E
        """
        letters_count = len(tile_type_letter)
        for i in range(letters_count-1):
            if tile_type_letter[i][0] > tile_type_letter[i+1][0]:
                print(f"""On coordinates: {coordinate} \
                      there is wrong layers order: {tile_type_letter[i]}.""")
                raise WrongLayersOrderError

        """
        "Flag" mustn't be over the "Hole" or "Starting tile"
        """
        for i in range(len(tile_type_letter)-1):
            if tile_type_letter[i] == "B_hole" and tile_type_letter[i+1] == "D_flag" \
             or tile_type_letter[i] == "B_start_tile" and tile_type_letter[i+1] == "D_flag":
                print(f"""On coordinates: {coordinate} there is flag over \
                      hole or start: {tile_type_letter[i]}.""")
                raise FlagOnStartOrHoleError

        """
        Lasers cannot be in opposite direction: they would cover each other
        visually and give 2 x damages to robots.
        """
        if laser_count > 1:
            N_or_S = False
            W_or_E = False
            for tile in tiles_on_coordinate:
                if tile.type == "laser":
                    if (tile.direction == Direction.N or tile.direction == Direction.S):
                        if N_or_S:
                            print(f"Lasers in opposite directions on {coordinate}.")
                            raise LasersInOppositeDirectionError
                        else:
                            N_or_S = True
                    if (tile.direction == Direction.W or tile.direction == Direction.E):
                        if W_or_E:
                            print(f"Lasers in opposite directions on {coordinate}.")
                            raise LasersInOppositeDirectionError
                        else:
                            W_or_E = True

        """
        Lasers must start on wall tiles. Wall must be on the same coordinates
        as the laser base.
        """
        opposite_wall = False
        for tile in tiles_on_coordinate:
            if tile.name.startswith("laser_start"):
                # There must be wall in the opposite direction
                new_direction = tile.direction + Rotation(180)
                for tile_2 in tiles_on_coordinate:
                    if tile_2.type == "wall" and tile_2.direction == new_direction:
                        opposite_wall = True
                if not opposite_wall:
                    print(f"There is no wall at the start of laser on {coordinate}")
                    raise LasersWithoutWallError
            if tile.type == "flag":
                flags.append(tile.number)
            if tile.type == "start":
                starts.append(tile.number)

    """
    Flags and starts must be numbered from 1 to N, incremented +1.
    """
    flags.sort()
    starts.sort()
    for tiles_list in (flags, starts):
        if tiles_list != list(range(1, len(tiles_list) + 1)):
            print(tiles_list)
            print(list(range(1, len(tiles_list) + 1)))
            return NumberedTilesNotInOrderError

    return True
