"""
This file is called by Pytest test_loading.py
It checks that the maps have correct structure
Don't call it separately
"""

from loading import get_board
from util_backend import Direction, Rotation


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
        tile_type_letter = get_tiles(coordinate, tiles)
        check_count_of_tiles_types(tile_type_letter, coordinate)
        check_layers_order(tile_type_letter, coordinate)
        check_flag_is_not_on_hole_or_start(tile_type_letter, coordinate)
        laser_count = get_laser_count(tile_type_letter)
        if laser_count > 1:
            check_lasers_in_opposite_direction(
                tiles, coordinate
                )
        check_lasers_start(tiles, coordinate)
        flags_number, starts_number = get_flags_and_starts(
            tiles, flags, starts
        )
    sort_and_check_consecutive_numbers(flags_number)
    sort_and_check_consecutive_numbers(starts_number)

    # If none of above checks has raised an exception, validation is OK, so:
    return True


def get_tiles(coordinate, tiles):
    """
    Return tiles types for further processing.
    tile_type_letter - list of tiles' types according to order_tiles dictionary
    If there is the same tile twice on one coordinates, raise an exception.
    """
    tile_type_letter = []
    # seen_tiles is local variable to compare tiles list, it is not returned.
    seen_tiles = []
    for tile in tiles:
        tile_type_letter.append(get_order_tiles(type(tile).__name__))

        # Tiles with the same type and direction mustn't be in list of types
        if tile in seen_tiles:
            raise RepeatingTilesError(coordinate, tile.name)
        else:
            seen_tiles.append(tile)
    return tile_type_letter


def get_laser_count(tile_type_letter):
    """Return the count of laser tiles from given list."""
    laser_count = 0
    for letter in tile_type_letter:
        if letter == "E_laser":
            laser_count += 1
    return laser_count


def get_flags_and_starts(tiles, flags, starts):
    """Return the lists of numbers on flags and start tiles from the board."""
    for tile in tiles:
        if tile.type == "flag":
            flags.append(tile.number)
        if tile.type == "start":
            starts.append(tile.number)
    return flags, starts


def check_count_of_tiles_types(tile_type_letter, coordinate):
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
    ["A","B","D"] is correct, ["D", "A"] is not.
    A < B < C < D < E.
    """
    letters_count = len(tile_type_letter)
    for i in range(letters_count-1):
        if tile_type_letter[i][0] > tile_type_letter[i+1][0]:
            raise WrongLayersOrderError(coordinate, tile_type_letter[i])


def check_flag_is_not_on_hole_or_start(tile_type_letter, coordinate):
    """
    Take tiles` types list and check that flag never stands on hole or start.
    """
    hole_or_start_tile = False
    for letter in tile_type_letter:
        if letter == "B_hole" or letter == "B_start_tile":
            hole_or_start_tile = True
        if hole_or_start_tile and letter == "D_flag":
            raise FlagOnStartOrHoleError(coordinate, letter)


def check_lasers_in_opposite_direction(tiles, coordinate):
    """
    Lasers can not be in opposite direction: they would cover each other
    visually and give 2 x damages to robots.
    """
    N_or_S = False
    W_or_E = False
    for tile in tiles:
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


def check_lasers_start(tiles, coordinate):
    """
    Check that lasers start on wall tiles.
    Wall must be on the same coordinates as the laser base.
    """
    opposite_wall = False
    for tile in tiles:
        if tile.name.startswith("laser_start"):
            # There must be wall in the opposite direction
            new_direction = tile.direction + Rotation(180)
            for tile_2 in tiles:
                if tile_2.type == "wall" and tile_2.direction == new_direction:
                    opposite_wall = True
            if not opposite_wall:
                raise LasersWithoutWallError(coordinate)


def sort_and_check_consecutive_numbers(tiles_list):
    """
    Sort a list of numbers and check if it increments by 1 starting from 1.
    If it doesn't match the pattern, raise NumberedTilesNotInOrderError.
    """
    tiles_list.sort()
    if tiles_list != list(range(1, len(tiles_list) + 1)):
        raise NumberedTilesNotInOrderError(tiles_list)
