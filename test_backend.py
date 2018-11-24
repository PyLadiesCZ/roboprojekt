from backend import get_board, get_coordinates, get_data, get_tile_id, get_tile_rotation, Robot
import pytest

@pytest.mark.parametrize("map_name", ["test_1", "test_2", "test_3"])
def test_get_coordinates_returns_list(map_name):
    """Test that get_coordinates() returns a list for each map."""
    data = get_data("maps/" + map_name + ".json")
    coordinates = get_coordinates(data)
    assert isinstance(coordinates, list)


# Set of tests checking the structure of read JSON file (supposed to come from Tiled 1.2)
def test_map_returns_correct_data_list():
    """Take JSON file with test_1 map and assert correct data list.

    If the test_1.json map is changed or removed, the test needs to be updated."""
    data = get_data("maps/test_1.json")
    assert data["layers"][0]["data"] == [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]


@pytest.mark.parametrize(("id_number", "expected_value"),
                           [(0, 0),
                           (2, 2),
                           (4, 6),
                           (6, 9),
                           (13, 16),])
def test_map_returns_correct_image_ID(id_number, expected_value):
    """Take JSON file with test_1 map and assert correct image ID.

    If the test_1.json map is changed or removed, the test needs to be updated."""
    data = get_data("maps/test_1.json")
    assert data["tilesets"][0]["tiles"][id_number]["id"] == expected_value


@pytest.mark.parametrize(("id_number", "expected_value"),
                           [(0, "../img/squares/png/ground.png"),
                           (2, "../img/squares/png/laser_1_base.png"),
                           (4, "../img/squares/png/gear_r.png"),
                           (6, "../img/squares/png/pusher_1_3_5.png"),
                           (13, "../img/squares/png/laser_2.png"),])
def test_map_returns_correct_image_path(id_number, expected_value):
    """Take JSON file with test_1 map and assert correct image path.

    If the test_1.json map is changed or removed, the test needs to be updated."""
    data = get_data("maps/test_1.json")
    assert data["tilesets"][0]["tiles"][id_number]["image"] == expected_value


def test_get_board_instance():
    """ Take JSON file with test_3 map and assert correct tilelist is returned.

    If the test_3.json map is changed or removed, the test needs to be updated."""

    data = get_data("maps/test_3.json")
    board = get_board(data)
    assert isinstance(board, dict)

@pytest.mark.parametrize(("input_number", "converted_number"),
                         [(1, 1),
                         (2684354573, 13),
                         (2684354584, 24),
                         (1610612749, 13)])
def test_convert_tile_id(input_number, converted_number):
    """Take number from layer's data (JSON file) and assert it was correctly transformed to valid tile ID."""

    assert get_tile_id(input_number) == converted_number


@pytest.mark.parametrize(("input_number", "converted_number"),
                         [(1, 0),
                         (2684354573, 90),
                         (2684354584, 90),
                         (1610612749, 270),
                         (3221225497, 180)])
def test_convert_tile_rotation(input_number, converted_number):
    """Take number from layer's data (JSON file) and assert it was correctly transformed to valid rotation in degrees."""

    assert get_tile_rotation(input_number) == converted_number
    
@pytest.mark.parametrize(("input_coordinates", "input_rotation", "distance", "output_coordinates"),
                         [((3, 3), 0, 2, (3, 5)),
                          ((3, 3), 90, 2, (5, 3)),
                          ((3, 3), 180, 2, (3, 1)),
                          ((3, 3), 270, 2, (1, 3))])
def test_move_robot(input_coordinates, input_rotation, distance, output_coordinates):
    robot = Robot(input_rotation, None, input_coordinates)
    robot.move_robot(distance)
    assert robot.coordinates == output_coordinates



                          

