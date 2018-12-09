from backend import get_board, get_coordinates, get_data, get_tile_id, get_tile_rotation, Robot
import pytest
from pathlib import Path

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


def test_get_board_instance():
    """
    Take JSON file with test_3 map and assert correct tilelist is returned.

    If the test_3.json map is changed or removed, the test needs to be updated.
    """
    data = get_data("maps/test_3.json")
    board = get_board(data)
    assert isinstance(board, dict)


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
                         [(1, 0),
                         (2684354573, 90),
                         (2684354584, 90),
                         (1610612749, 270),
                         (3221225497, 180)])
def test_convert_tile_rotation(tile_number, converted_number):
    """
    Take number from layer's data (JSON file) and assert it was correctly
    transformed to valid rotation in degrees.
    """
    assert get_tile_rotation(tile_number) == converted_number


@pytest.mark.parametrize(("input_coordinates", "input_rotation", "distance", "output_coordinates"),
                         [((3, 3), 0, 2, (3, 5)),
                          ((3, 3), 90, 2, (5, 3)),
                          ((3, 3), 180, 2, (3, 1)),
                          ((3, 3), 270, 2, (1, 3))])
def test_robot_walk(input_coordinates, input_rotation, distance, output_coordinates):
    """
    Take robot's coordinates, rotation and distance and assert robot walked
    to correct coordinates.
    """
    robot = Robot(input_rotation, None, input_coordinates)
    robot.walk(distance)
    assert robot.coordinates == output_coordinates


@pytest.mark.parametrize(("input_coordinates", "input_direction", "distance", "output_coordinates"),
                         [((3, 3), 0, 2, (3, 5)),
                          ((3, 3), 90, 2, (5, 3)),
                          ((3, 3), 180, 2, (3, 1)),
                          ((3, 3), 270, 2, (1, 3))])
def test_robot_move(input_coordinates, input_direction, distance, output_coordinates):
    """
    Take robot's coordinates, move's direction and distance and assert robot
    was moved to correct coordinates.
    """
    robot = Robot(0, None, input_coordinates)
    robot.move(input_direction, distance)
    assert robot.coordinates == output_coordinates


def type_index(type, tiles):
    for i, tile in enumerate(tiles):
        if tile.type == type:
            return i
    raise LookupError(type)


def get_order_squares(text):
    order_squares = {
    'ground':"A",
    'hole':"B",
    'starting_square':"B",
    'repair':"B",
    'belt':"B",
    'gear':"B",
    'flag':"C",
    'pusher':"D",
    'laser':"D",
    'wall':"D"}
    for key, value in order_squares.items():
        return order_squares.get(text)

def img_list(map_name):
    data = get_data("maps/" + map_name + ".json")
    board = get_board(data)

    for key, value in board.items():
        square_type = []
        for i in value:
            square_type.append( get_order_squares(i.type)[0])
        a = 0
        b = 0
        c = 0
        for letter in square_type:
            if letter == 'A':
                a += 1
            if letter == 'B':
                b += 1
            if letter == 'C':
                c += 1
        if a > 1 or b > 1 or c > 1:
            return False
    b = len(square_type)
    if b < 6:
        for i in range(b, 6):
            square_type.append('Z')
        print(a)
    if square_type[0] <= square_type[1] <= square_type[2] <= square_type[3] <= square_type[4] <= square_type[5]:
        return True
    else:
        return square_type

@pytest.mark.parametrize("map_name", ["test_7","test_6", "test_5", "test_3"])
def test_map_is_valid(map_name):
    assert img_list(map_name) == True
