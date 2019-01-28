from util import Tile, HoleTile, WallTile, GearTile, PusherTile, LaserTile, StartTile, Direction
from loading import get_data, get_tile_id, get_tile_direction, get_board
from pathlib import Path
from validator import check_squares
import pytest


maps = []
"""
Create a list of all maps.
To be used as an argument for the functions which need to go through all maps so they don't need to be added manually.
"""
for i in Path('maps/').glob('test_*.json'):
    maps.append(str(i))


# Set of tests checking the structure of read JSON file (supposed to come from Tiled 1.2)
@pytest.mark.parametrize(("coordinates", "layer", "type"),
                         [((5, 5), 0, HoleTile),
                          ((0, 0), 0, HoleTile),
                          ((11, 11), 0, HoleTile),
                          ((2, 1), 0, Tile),
                          ((11, 10), 0, Tile)])
def test_map_1_contains_correct_fields(coordinates, layer, type):
    """
    Take JSON file with test_1 map and assert the correct field types.
    If the test_1.json map is changed or removed, the test needs to be updated.
    """
    board = get_board("maps/test_1.json")
    assert isinstance(board[coordinates][layer], type)


@pytest.mark.parametrize(("coordinates", "layer", "type"),
                         [((5, 5), 0, WallTile),
                          ((0, 0), 0, LaserTile),
                          ((11, 11), 0, GearTile),
                          ((2, 1), 0, StartTile),
                          ((11, 10), 0, PusherTile)])
def test_map_1_does_not_contain_incorrect_fields(coordinates, layer, type):
    """
    Take JSON file with test_1 map and assert it doesn't contain the incorrect field types (inheritance of Tile class is OK).
    If the test_1.json map is changed or removed, the test needs to be updated.
    """
    board = get_board("maps/test_1.json")
    assert not isinstance(board[coordinates][layer], type)


@pytest.mark.parametrize(("index_number", "expected_value"),
                         [(0, 0),
                          (2, 2),
                          (4, 6),
                          (6, 9),
                          (13, 17), ])
def test_map_returns_correct_image_ID(index_number, expected_value):
    """
    Take JSON file with test_1 map and assert correct image ID.
    index_number: tiles list instance index
    expected value: "id" stored in tiles list
    If the test_1.json map is changed or removed, the test needs to be updated.
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
    Take JSON file with test_1 map and assert correct image path.
    index_number: tiles list instance index
    expected value: "image" stored in tiles list
    If the test_1.json map is changed or removed, the test needs to be updated.
    """
    data = get_data("maps/test_1.json")
    assert data["tilesets"][0]["tiles"][index_number]["image"] == expected_value


def test_board_structure():
    """
    Take board (based on JSON test_3 map) and assert correct board structure is returned.
    If the test_3.json map is changed or removed, the test needs to be updated.
    """
    board = get_board("maps/test_3.json")
    example_tile = board[0, 0]
    assert example_tile[0].path == "./img/squares/png/ground.png"
    assert example_tile[0].direction == Direction.N


@pytest.mark.parametrize(("tile_number", "converted_number"),
                         [(1, 1),
                         (2684354573, 13),
                         (2684354584, 24),
                         (1610612749, 13)])
def test_convert_tile_id(tile_number, converted_number):
    """
    Take number from layer's data (JSON file) and assert it was correctly
    transformed to valid tile ID.
    """
    assert get_tile_id(tile_number) == converted_number


@pytest.mark.parametrize(("tile_number", "converted_number"),
                         [(1, Direction.N),
                         (2684354573, Direction.E),
                         (2684354584, Direction.E),
                         (1610612749, Direction.W),
                         (3221225497, Direction.S)])
def test_convert_tile_direction(tile_number, converted_number):
    """
    Take number from layer's data (JSON file) and assert it was correctly
    transformed to valid direction in degrees.
    """
    assert get_tile_direction(tile_number) == converted_number


@pytest.mark.parametrize("map_name", maps)
def test_tile_size(map_name):
    """
    Take size of tiles used in JSON files and assert correct tile size.
    This test has to be removed, when width and height of tile image are
    no longer constants used for tile drawing.
    """
    data = get_data(map_name)
    assert data["tilewidth"] == 64
    assert data["tileheight"] == 64


@pytest.mark.parametrize("map_name", maps)
def test_map_is_valid(map_name):
    """Use validator to check all the valid maps are correctly layered, therefore accepted."""

    assert check_squares(map_name) == True


@pytest.mark.parametrize("map_name", ["maps/bad_map.json"])
def test_map_is_invalid(map_name):
    """Use validator to check the invalid map is not accepted."""

    assert check_squares(map_name) != True
