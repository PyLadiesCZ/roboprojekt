from backend import  get_starting_coordinates, get_robot_paths, get_robots_to_start, get_start_state, Robot, State, MovementCard, RotationCard
from util import Tile, HoleTile, WallTile, GearTile, PusherTile, LaserTile, StartTile, Direction, Rotation
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


def test_starting_coordinates():
    """
    Take board (based on JSON test_3 map) and assert correct starting coordinates are returned.
    If the test_3.json map is changed or removed, the test needs to be updated.
    """
    board = get_board("maps/test_3.json")
    assert len(get_starting_coordinates(board)) == 8
    assert isinstance(get_starting_coordinates(board), list)


def test_robot_paths():
    """
    Get list of robot paths, assert that instance of the list is Path object. The list will change in time, it is not possible to test length or all the paths.
    """
    robot_paths = get_robot_paths()
    path, path_front = robot_paths[0]
    assert isinstance(robot_paths, list)
    assert isinstance(path, Path)


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


def test_robots_on_starting_coordinates():
    """
    Assert that the result of get_robots_to_start is a list which contains Robot objects with correct attribute coordinates.
    """
    board = get_board("maps/test_3.json")
    robots = get_robots_to_start(board)
    assert isinstance(robots, list)
    assert isinstance(robots[0], Robot)


def test_starting_state():
    """
    Assert that created starting state (board and robots) contains the correct instances of objects.
    """
    ss = get_start_state("maps/test_3.json")
    assert isinstance(ss, State)
    assert isinstance(ss.robots, list)
    assert isinstance(ss.robots[0], Robot)
    assert isinstance(ss._board, dict)
    assert isinstance(ss._board[0, 0], list)
    assert isinstance(ss._board[0, 0][0], Tile)


@pytest.mark.parametrize(("input_coordinates", "input_direction", "distance", "output_coordinates"),
                         [((3, 3), Direction.N, 2, (3, 5)),
                          ((3, 3), Direction.E, 2, (3, 3)),
                          ((3, 3), Direction.S, 2, (3, 2)),
                          ((3, 3), Direction.W, 2, (2, 3)),
                          ((5, 1), Direction.E, 2, (7, 1))])
def test_robot_walk(input_coordinates, input_direction, distance, output_coordinates):
    """
    Take robot's coordinates, direction and distance and assert robot walked
    to correct coordinates.
    """
    state = get_start_state("maps/test_3.json")
    robot = Robot(input_direction, None, None, input_coordinates)
    robot.walk(distance, state, input_direction)
    assert robot.coordinates == output_coordinates


@pytest.mark.parametrize(("input_coordinates", "input_direction", "distance", "output_coordinates"),
                         [((0, 1), Direction.N, 3, (0, 4)),
                          ((8, 1), Direction.N, 3, (8, 3)),
                          ((10, 1), Direction.N, 3, (10, 2)),
                          ((3, 3), Direction.E, 2, (3, 3)),
                          ((3, 3), Direction.S, 2, (3, 2)),
                          ((3, 3), Direction.W, 2, (2, 3)),
                          ((5, 1), Direction.E, 2, (5, 1))])
def test_robot_move(input_coordinates, input_direction, distance, output_coordinates):
    """
    Take robot's coordinates, move's direction and distance and assert robot
    was moved to correct coordinates.
    """
    state = get_start_state("maps/test_3.json")
    robot = Robot(Direction.N, None, None, input_coordinates)
    robot.move(input_direction, distance, state)
    assert robot.coordinates == output_coordinates


@pytest.mark.parametrize(("current_direction", "towards", "new_direction"),
                        [(Direction.N, Rotation.LEFT, Direction.W),
                         (Direction.S, Rotation.RIGHT, Direction.W),
                         (Direction.E, Rotation.U_TURN, Direction.W)])
def test_robot_change_direction(current_direction, towards, new_direction):
    """
    Assert that robot rotates correctly according to given rotation.
    """
    robot = Robot(current_direction, None, None, None)
    robot.rotate(towards)
    assert robot.direction == new_direction


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

@pytest.mark.parametrize(("card", "new_coordinates"),
                        [(MovementCard(100, 1), (5, 6)),
                         (MovementCard(100, 2), (5, 7)),
                         (MovementCard(100, 3), (5, 8)),
                         (MovementCard(100, -1), (5, 4)),
                         ])
def test_move_cards(card, new_coordinates):
    robot = Robot(Direction.N, None, None, (5, 5))
    robot.program = [card]
    state = get_start_state("maps/test_3.json")
    robot.apply_card_effect(state)
    assert robot.coordinates == new_coordinates
