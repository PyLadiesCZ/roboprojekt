from backend import get_board, get_coordinates, get_data, get_tile_id, get_tile_direction, get_paths, get_starting_coordinates, get_robot_paths, get_robots_to_start, get_start_state, Robot, State, Tile, Direction
from pathlib import Path
from validator import img_list
import pytest

@pytest.mark.parametrize("map_name", ["test_1", "test_2", "test_3"])
def test_get_coordinates_returns_list(map_name):
    """Test that get_coordinates() returns a list for each map."""
    data = get_data("maps/" + map_name + ".json")
    coordinates = get_coordinates(data)
    assert isinstance(coordinates, list)


# Set of tests checking the structure of read JSON file (supposed to come from Tiled 1.2)
def test_map_returns_correct_data_list():
    """
    Take JSON file with test_1 map and assert correct data list.
    If the test_1.json map is changed or removed, the test needs to be updated.
    """
    data = get_data("maps/test_1.json")
    assert data["layers"][0]["data"] == [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]


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
    data = get_data("maps/test_3.json")
    board = get_board(data)
    example_tile = board[0, 0]
    assert example_tile[0].path == "./img/squares/png/ground.png"
    assert example_tile[0].direction == Direction.N


def test_starting_coordinates():
    """
    Take board (based on JSON test_3 map) and assert correct starting coordinates are returned.
    If the test_3.json map is changed or removed, the test needs to be updated.
    """
    data = get_data("maps/test_3.json")
    board = get_board(data)
    assert len(get_starting_coordinates(board)) == 8
    assert isinstance(get_starting_coordinates(board), list)


def test_robot_paths():
    """
    Get list of robot paths, assert that instance of the list is Path object. The list will change in time, it is not possible to test length or all the paths.
    """
    robot_paths = get_robot_paths()
    assert isinstance(robot_paths, list)
    assert isinstance(robot_paths[0], Path)


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


def test_dict_paths_is_correct():
    """
    Assert that the result of get_paths() is a dictionary.
    Assert that the paths structure is valid: integer is tile ID, string is path to the picture.
    """
    data = get_data("maps/test_3.json")
    paths = get_paths(data)
    for key, value in paths.items():
        assert isinstance(key, int)
        assert isinstance(value, str)
    assert isinstance(paths, dict)


def test_robots_on_starting_coordinates():
    """
    Assert that the result of get_robots_to_start is a list which contains Robot objects with correct attribute coordinates.
    """
    data = get_data("maps/test_3.json")
    board = get_board(data)
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
    assert isinstance(ss.board, dict)
    assert isinstance(ss.board[0, 0], list)
    assert isinstance(ss.board[0, 0][0], Tile)


@pytest.mark.parametrize(("input_coordinates", "input_direction", "distance", "output_coordinates"),
                         [((3, 3), Direction.N, 2, (3, 5)),
                          ((3, 3), Direction.E, 2, (5, 3)),
                          ((3, 3), Direction.S, 2, (3, 1)),
                          ((3, 3), Direction.W, 2, (1, 3))])
def test_robot_walk(input_coordinates, input_direction, distance, output_coordinates):
    """
    Take robot's coordinates, direction and distance and assert robot walked
    to correct coordinates.
    """
    robot = Robot(input_direction, None, input_coordinates)
    robot.walk(distance)
    assert robot.coordinates == output_coordinates


@pytest.mark.parametrize(("input_coordinates", "input_direction", "distance", "output_coordinates"),
                         [((3, 3), Direction.N, 2, (3, 5)),
                          ((3, 3), Direction.E, 2, (5, 3)),
                          ((3, 3), Direction.S, 2, (3, 1)),
                          ((3, 3), Direction.W, 2, (1, 3))])
def test_robot_move(input_coordinates, input_direction, distance, output_coordinates):
    """
    Take robot's coordinates, move's direction and distance and assert robot
    was moved to correct coordinates.
    """
    robot = Robot(Direction.N, None, input_coordinates)
    robot.move(input_direction, distance)
    assert robot.coordinates == output_coordinates


@pytest.mark.parametrize("map_name", ["test_1", "test_2", "test_3", "test_4"])
def test_tile_size(map_name):
    """
    Take size of tiles used in JSON files and assert correct tile size.
    This test has to be removed, when width and height of tile image are
    no longer constants used for tile drawing.
    """
    data = get_data("maps/" + map_name + ".json")
    assert data["tilewidth"] == 64
    assert data["tileheight"] == 64

@pytest.mark.parametrize("map_name", ["test_3", "test_5"])
def test_map_is_valid(map_name):
    assert img_list(map_name) == True
