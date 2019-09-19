"""
Unit tests for validator.py
"""
import pytest

from loading import get_board
from validator import get_tiles, get_laser_count, get_flags_and_starts
from validator import check_count_of_tiles_types, check_layers_order
from validator import check_flag_is_not_on_hole_or_start
from validator import sort_and_check_consecutive_numbers
from validator import NumberedTilesNotInOrderError, WrongLayersOrderError
from validator import FlagOnStartOrHoleError, RepeatingTilesError
from validator import TilesOfOneTypeError


def test_numbers_are_consecutive():
    """ Assert list of consecutive numbers is given. """
    tiles_list = [5, 2, 4, 3, 1]
    assert sort_and_check_consecutive_numbers(tiles_list) is None


def test_flag_numbers_are_inconsecutive():
    """
    List of inconsecutive numbers raises NumberedTilesNotInOrderError.
    """
    tiles_list = [5, 8, 3, 2]
    with pytest.raises(NumberedTilesNotInOrderError):
        sort_and_check_consecutive_numbers(tiles_list)


@pytest.mark.parametrize(("tiles_layers"),
                         [["D_flag", "C_repair"],
                          ["E_laser", "A_ground"],
                          ["E_wall", "C_belt"]])
def test_layers_are_incorrect(tiles_layers):
    """ Incorrect order of map layers raises WrongLayersOrderError. """
    with pytest.raises(WrongLayersOrderError):
        check_layers_order(tiles_layers, (1, 1))


@pytest.mark.parametrize(("tiles_layers"),
                         [["C_repair", "D_flag"],
                          ["A_ground", "E_laser"],
                          ["C_belt", "E_wall"]])
def test_layers_are_correct(tiles_layers):
    """ Assert correct order of map layers passes OK. """
    assert check_layers_order(tiles_layers, (1, 1)) is None


@pytest.mark.parametrize(("tiles_layers"),
                         [["B_hole", "D_flag"],
                          ["B_start_tile", "D_flag"]])
def test_flag_on_hole_start_is_incorrect(tiles_layers):
    """ Raise FlagOnStartOrHoleError when flag is placed on start or hole. """
    with pytest.raises(FlagOnStartOrHoleError):
        check_flag_is_not_on_hole_or_start(tiles_layers, (1, 1))


@pytest.mark.parametrize(("tiles_layers"),
                         [["C_repair", "D_flag", "C_gear"],
                          ["D_flag", "C_belt", "E_wall"],
                          ["A_ground", "D_flag", "E_pusher"]])
def test_flag_on_correct_tiles(tiles_layers):
    """ Assert flag placed on any tile except start and hole passes OK. """
    assert check_flag_is_not_on_hole_or_start(tiles_layers, (1, 1)) is None


@pytest.mark.parametrize(("tiles_layers"),
                         [["C_gear", "D_flag", "C_repair"],
                          ["C_belt", "C_repair", "E_wall"],
                          ["C_belt", "B_start_tile", "B_hole"],
                          ["C_belt", "B_hole", "C_repair"],
                          ["B_start_tile", "C_belt", "B_start_tile"],
                          ["A_ground", "A_ground", "E_pusher"]])
def test_count_of_tiles_is_invalid(tiles_layers):
    """ Raise TilesOfOneTypeError when more tiles from A, B, C groups are placed
    on one coordinates. """
    with pytest.raises(TilesOfOneTypeError):
        check_count_of_tiles_types(tiles_layers, (1, 1))


@pytest.mark.parametrize(("tiles_layers"),
                         [["C_repair", "D_flag", "B_hole"],
                          ["D_flag", "C_belt", "E_wall"],
                          ["A_ground", "D_flag", "E_pusher"]])
def test_count_of_tiles_is_valid(tiles_layers):
    """ Assert that one tile of groups A, B, C on coordinates passes OK. """
    assert check_count_of_tiles_types(tiles_layers, (1, 1)) is None


@pytest.mark.parametrize(("tiles_layers", "count"),
                         [(["E_pusher", "E_laser", "E_laser"], 2),
                          (["D_flag", "E_laser", "E_wall"], 1),
                          (["E_laser", "E_laser", "E_laser"], 3),
                          (["D_flag", "C_belt", "E_wall"], 0)])
def test_count_of_lasers_is_valid(tiles_layers, count):
    """ Assert count of lasers on given list of tiles is correct. """
    assert get_laser_count(tiles_layers) == count


def test_get_flags_starts():
    """ Assert count of start and flags tiles is computed correctly. """
    board = get_board("./maps/test_6.json")
    f = []
    s = []
    for coordinate, tiles in board.items():
        flags, starts = get_flags_and_starts(tiles, f, s)
    assert len(flags) == 1
    assert len(starts) == 1


def test_get_tiles_raises_exception():
    """ Raise RepeatingTilesError when the same tile is placed twice
    on one coordinates. """
    board = get_board("./maps/bad_maps/bad_2.json")
    for coordinate, tiles in board.items():
        with pytest.raises(RepeatingTilesError):
            get_tiles(coordinate, tiles)


def test_get_tiles():
    """ Assert the tiles are correctly matched to their types. """
    board = get_board("./maps/test_6.json")
    ttl_1_1 = get_tiles((1, 1), board[(1, 1)])
    ttl_2_2 = get_tiles((2, 2), board[(2, 2)])
    assert ttl_1_1 == ['A_ground', 'E_laser', 'E_wall']
    assert ttl_2_2 == ['A_ground', 'C_repair']
