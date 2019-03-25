"""
Tests checking the structure of read JSON file.

(map files are supposed to come from Tiled 1.2's JSON export)
"""

import pytest
from pathlib import Path

from loading import get_data, get_tile_id, get_tile_direction, get_board
from util import Direction
from tile import Tile, HoleTile
from validator import check_squares


# List of paths to valid test maps.
# To be used as an argument for check_squares which checks validity of all maps
VALID_MAPS_PATHS = []
for map_path in Path("maps/").glob("test_*.json"):
    VALID_MAPS_PATHS.append(str(map_path))


@pytest.mark.parametrize("map_name", VALID_MAPS_PATHS)
def test_map_is_valid(map_name):
    """
    Use validator to check all the valid maps are correctly layered, therefore accepted.
    """
    assert check_squares(map_name) is True


@pytest.mark.parametrize("map_name", ["maps/bad_map.json"])
def test_map_is_invalid(map_name):
    """
    Use validator to check the invalid map is not accepted.
    """
    assert check_squares(map_name) is not True


@pytest.mark.parametrize(
    ("coordinates", "tile_type"),
    [
         # Tile on the diagonal is hole
         ((5, 5), HoleTile),

         # Centers of all 4 edges
         ((0, 5), HoleTile),
         ((5, 0), HoleTile),
         ((11, 5), Tile),
         ((5, 11), Tile),
    ]
)
def test_map_1_is_right_oriented(coordinates, tile_type):
    """
    Test maps are loaded in the right orientation.

    Uses test_1.json map for this.
    """
    board = get_board("maps/test_1.json")
    assert isinstance(board[coordinates][0], tile_type)


@pytest.mark.parametrize(
    ("index_number", "expected_value"),
    [
        (0, 0),
        (2, 2),
        (4, 6),
        (6, 9),
        (13, 17),
    ]
)
def test_map_returns_correct_image_ID(index_number, expected_value):
    """
    Test the loaded map file returns expected image ID.

    Regression test of get_data function. Uses test_1.json map for this.
    """
    data = get_data("maps/test_1.json")
    assert data["tilesets"][0]["tiles"][index_number]["id"] == expected_value


@pytest.mark.parametrize(("index_number", "expected_value"),
                         [(0, "../img/squares/png/ground.png"),
                          (2, "../img/squares/png/laser_1_base.png"),
                          (4, "../img/squares/png/gear_r.png"),
                          (6, "../img/squares/png/pusher_1_3_5.png"),
                          (13, "../img/squares/png/conveyor_belt_1.png"), ])
def test_map_returns_correct_image_path(index_number, expected_value):
    """
    Test the loaded map file returns expected image path.

    Regression test of get_data function. Uses test_1.json map for this.
    """
    data = get_data("maps/test_1.json")
    assert data["tilesets"][0]["tiles"][index_number]["image"] == expected_value


def test_board_structure():

    pass


CONVERT_TEST_DATA = {
    1: {
        "tile": 1,
        "direction": Direction.N,
    },
    2684354573: {
        "tile": 13,
        "direction": Direction.E,
    },
    2684354584: {
        "tile": 24,
        "direction": Direction.E,
    },
    1610612749: {
        "tile": 13,
        "direction": Direction.W,
    },
    3221225497: {
        "tile": 25,
        "direction": Direction.S,
    },
}


@pytest.mark.parametrize(("test_case"), CONVERT_TEST_DATA)
def test_convert_tile_id(test_case):
    """
    Take number from layer's data (JSON file) and assert it was correctly
    transformed to valid tile ID.
    """
    tile_number = test_case
    assert get_tile_id(tile_number) == CONVERT_TEST_DATA[test_case]["tile"]


@pytest.mark.parametrize(("test_case"), CONVERT_TEST_DATA)
def test_convert_tile_direction(test_case):
    """
    Take number from layer's data (JSON file) and assert it was correctly
    transformed to valid direction.
    """
    tile_number = test_case
    assert get_tile_direction(tile_number) == CONVERT_TEST_DATA[test_case]["direction"]
