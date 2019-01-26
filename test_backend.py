from backend import get_starting_coordinates, get_robot_paths, get_robots_to_start, get_start_state, Robot, State, MovementCard, RotationCard, apply_tile_effects
from util import Tile, HoleTile, WallTile, GearTile, PusherTile, LaserTile, StartTile, RepairTile, Direction, Rotation
from loading import get_board
from pathlib import Path
import pytest


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


@pytest.mark.parametrize(("damages_before", "tile", "damages_after"),
                        [(0, RepairTile(None, None, [{'value': True}]), 0),
                         (9, RepairTile(None, None, [{'value': True}]), 8),
                         (3, RepairTile(None, None, [{'value': True}]), 2),
                        ])
def test_robot_is_repaired(damages_before, tile, damages_after):
    robot = Robot(None, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], 1)
    robot.damages = damages_before
    apply_tile_effects(state)
    assert robot.damages == damages_after


@pytest.mark.parametrize(("tile", "coordinates_after"),
                        [(RepairTile(None, None, [{'value': True}]),  (0, 0)),
                         (RepairTile(None, None, [{'value': False}]), (1, 1)),
                         (RepairTile(None, None, [{'value': True}]), (0, 0)),
                         (RepairTile(None, None, [{'value': False}]), (1, 1)),
                        ])
def test_robot_changed_start_coordinates(tile, coordinates_after):
    robot = Robot(None, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], 1)
    robot.start_coordinates = (1, 1)
    apply_tile_effects(state)
    assert robot.start_coordinates == coordinates_after


@pytest.mark.parametrize(("card", "new_coordinates"),
                        [(MovementCard(100, 1), (5, 6)),
                         (MovementCard(100, 2), (5, 7)),
                         (MovementCard(100, 3), (5, 8)),
                         (MovementCard(100, -1), (5, 4)),
                         ])
def test_move_cards(card, new_coordinates):
    """
    Give mock robot the MovementCard and check if he moved to the expected coordinates.
    """
    robot = Robot(Direction.N, None, None, (5, 5))
    robot.program = [card]
    state = get_start_state("maps/test_3.json")
    robot.apply_card_effect(state)
    assert robot.coordinates == new_coordinates


@pytest.mark.parametrize(("card", "new_direction"),
                        [(RotationCard(100, Rotation.LEFT), Direction.W),
                         (RotationCard(100, Rotation.RIGHT), Direction.E),
                         (RotationCard(100, Rotation.U_TURN), Direction.S),
                         ])
def test_rotate_cards(card, new_direction):
    """
    Give mock robot the RotationCard and check if he's heading to the expected direction.
    """
    robot = Robot(Direction.N, None, None, None)
    robot.program = [card]
    state = get_start_state("maps/test_3.json")
    robot.apply_card_effect(state)
    assert robot.direction == new_direction
