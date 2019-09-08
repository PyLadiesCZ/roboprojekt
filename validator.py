"""
This file is called by Pytest test_loading.py
It checks that the maps have correct structure
Don't call it separately
"""

from loading import get_board
from util import Direction, Rotation


class RepeatingTilesError(Exception):
    """Raised when there are two the same tiles on the same coordinates."""
    def __init__(self, coordinates, tiles):
        self.coordinates = coordinates
        self.tiles = tiles

    def __str__(self):
        return f"""On coordinates: {self.coordinates} there is this tile twice: \
{self.tiles}. The tiles mustn't repeat."""


class WrongLayersOrderError(Exception):
    """
    Raised when the layers are in the incorrect order which may lead to
    covering visible elements of the map.
    """
    def __init__(self, coordinates, tiles_letter):
        self.coordinates = coordinates
        self.tiles_letter = tiles_letter

    def __str__(self):
        return f"""On coordinates: {self.coordinates} there is wrong layers order: \
{self.tiles_letter}."""


class TilesOfOneTypeError(Exception):
    """
    Raised when there is too many tiles of one type on the same coordinates.
    Eg. Repair or gear tile mustn't repeat, there may be one only.
    """
    def __init__(self, details, layers):
        self.coordinates = details
        self.layers = layers

    def __str__(self):
        return f"""On coordinates: {self.coordinates} there is this count of \
tiles: a-{self.layers[0]}, b-{self.layers[1]}, c-{self.layers[2]}, d-{self.layers[3]}. \
There must be only one of tile from those types."""


class FlagOnStartOrHoleError(Exception):
    """Raised when flag covers start or hole tile."""
    def __init__(self, coordinates, tiles_letter):
        self.coordinates = coordinates
        self.tiles_letter = tiles_letter

    def __str__(self):
        return f"""On coordinates: {self.coordinates} there there is flag over \
hole or start: {self.tiles_letter}."""


class LasersInOppositeDirectionError(Exception):
    """
    Raised when lasers are heading opposite directions,
    therefore are not visible.
    """
    def __init__(self, coordinates):
        self.coordinates = coordinates

    def __str__(self):
        return f"Lasers in opposite directions on {self.coordinates}."


class LasersWithoutWallError(Exception):
    """Raised when there is no wall at the beginning of the laser."""
    def __init__(self, coordinates):
        self.coordinates = coordinates

    def __str__(self):
        return f"There is no wall at the start of laser on {self.coordinates}."


class NumberedTilesNotInOrderError(Exception):
    """Raised when numbered tiles like flags or starts are either:
    - not in order (eg. 1, 2, 6, 7)
    - starting from different number than 1 (eg. 0, 1, 2 or 5, 6, 7)
    """
    def __init__(self, tiles_list):
        self.tiles_list = tiles_list

    def __str__(self):
        return f"""The list {self.tiles_list} should look like this""",
        list(range(1, len(self.tiles_list) + 1))


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
        tile_type_letter, tiles_on_coordinate = get_tiles(coordinate, tiles)
        check_count_of_tiles(tile_type_letter, coordinate)
        check_layers_order(tile_type_letter, coordinate)
        check_flag_is_not_on_hole_or_start(tile_type_letter, coordinate)
        laser_count = get_laser_count(tile_type_letter)
        check_lasers_in_opposite_direction(
            laser_count, tiles_on_coordinate, coordinate
        )
        check_lasers_start(tiles_on_coordinate, coordinate)
        flags_number, starts_number = get_flags_and_starts(
            tiles_on_coordinate, flags, starts
        )
    check_consecutive_numbers(flags_number)
    check_consecutive_numbers(starts_number)

    # If none of above checks has raised and exception, validation is OK, so:
    return True


def get_tiles(coordinate, tiles):
    """
    Gather the tiles on given coordinates to two lists:
    tile_type_letter - list of tiles' types according to order_tiles dictionary
    tiles_on_coordinate - list of tiles on the same coordinates.
    If there is the same tile twice, raise exception.
    """
    tile_type_letter = []
    tiles_on_coordinate = []
    for tile in tiles:
        tile_type_letter.append(get_order_tiles(type(tile).__name__))
        """
        Tiles with the same type and direction mustn't be in list of types
        """
        if tile in tiles_on_coordinate:
            raise RepeatingTilesError(coordinate, tile.name)
        else:
            tiles_on_coordinate.append(tile)
    return tile_type_letter, tiles_on_coordinate


def get_laser_count(tile_type_letter):
    """Return the count of laser tiles on given coordinates."""
    laser_count = 0
    for letter in tile_type_letter:
        if letter == "E_laser":
            laser_count += 1
    return laser_count


def get_flags_and_starts(tiles_on_coordinate, flags, starts):
    """Return the list of flag and start tiles on given coordinates."""
    for tile in tiles_on_coordinate:
        if tile.type == "flag":
            flags.append(tile.number)
        if tile.type == "start":
            starts.append(tile.number)
    return flags, starts


def check_count_of_tiles(tile_type_letter, coordinate):
    """
    Check there is only one tile of type A, B, C or D on the same coordinates.
    If there is more than one, raise exception.
    """
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
        raise TilesOfOneTypeError(coordinate, (a, b, c, d))


def check_layers_order(tile_type_letter, coordinate):
    """
    Tiles types must be in the correct order.
    ["A","B","D"] is correct ["D", "A"] is not
    A < B < C < D < E
    """
    letters_count = len(tile_type_letter)
    for i in range(letters_count-1):
        if tile_type_letter[i][0] > tile_type_letter[i+1][0]:
            raise WrongLayersOrderError(coordinate, tile_type_letter[i])


def check_flag_is_not_on_hole_or_start(tile_type_letter, coordinate):
    """
    "Flag" mustn't be over the "Hole" or "Starting tile"
    """
    for i in range(len(tile_type_letter)-1):
        if tile_type_letter[i] == "B_hole" and tile_type_letter[i+1] == "D_flag" \
         or tile_type_letter[i] == "B_start_tile" and tile_type_letter[i+1] == "D_flag":
            raise FlagOnStartOrHoleError(coordinate, tile_type_letter[i])


def check_lasers_in_opposite_direction(laser_count, tiles_on_coordinate, coordinate):
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
                        raise LasersInOppositeDirectionError(coordinate)
                    else:
                        N_or_S = True
                if (tile.direction == Direction.W or tile.direction == Direction.E):
                    if W_or_E:
                        raise LasersInOppositeDirectionError(coordinate)
                    else:
                        W_or_E = True


def check_lasers_start(tiles_on_coordinate, coordinate):
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
                raise LasersWithoutWallError(coordinate)


def check_consecutive_numbers(tiles_list):
    """
    Flags and starts must be numbered from 1 to N, incremented +1.
    """
    tiles_list.sort()
    if tiles_list != list(range(1, len(tiles_list) + 1)):
        raise NumberedTilesNotInOrderError(tiles_list)
