from backend import get_starting_coordinates, get_robot_paths, get_robots_to_start, get_start_state, Robot, State, MovementCard, RotationCard, apply_tile_effects
from util import Tile, HoleTile, WallTile, GearTile, PusherTile, LaserTile, StartTile, RepairTile, FlagTile, Direction, Rotation
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


# RepairTile

@pytest.mark.parametrize(("damages_before", "tile", "damages_after"),
                        [(0, RepairTile(None, None, [{'value': True}]), 0),
                         (9, RepairTile(None, None, [{'value': True}]), 8),
                         (3, RepairTile(None, None, [{'value': True}]), 2),
                        ])
def test_robot_is_repaired(damages_before, tile, damages_after):
    """
    When robot is on RepairTile he is supposed to be repaired.
    If he doesn't have any damages, the count remains the same as previous.
    """
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
    """
    When robot is on RepairTile with special property, he changes it starting coordinates to the tile coordinates.
    On a normal RepairTile he doesn't change the starting tile.
    """
    robot = Robot(None, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], 1)
    robot.start_coordinates = (1, 1)
    apply_tile_effects(state)
    assert robot.start_coordinates == coordinates_after


# GearTile

@pytest.mark.parametrize(("direction_before", "tile", "direction_after"),
                        [(Direction.E, GearTile(None, None, [{'value': "left"}]),  Direction.N),
                         (Direction.E, GearTile(None, None, [{'value': "right"}]), Direction.S),
                         (Direction.S, GearTile(None, None, [{'value': "left"}]), Direction.E),
                         (Direction.S, GearTile(None, None, [{'value': "right"}]), Direction.W),
                        ])
def test_robot_changed_direction(direction_before, tile, direction_after):
    """
    When robot is on GearTile, he should be rotated according to the direction of the tile.
    Check that his direction changed after applying tile effect.
    """
    robot = Robot(direction_before, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], 1)
    apply_tile_effects(state)
    assert robot.direction == direction_after


# HoleTile hidden in walk method

@pytest.mark.parametrize(("lives_before", "tile", "lives_after", "active", "coordinates"),
                        [(3, HoleTile(None, None, None),  2, True, (-1, -1)),
                         (2, HoleTile(None, None, None),  1, True, (-1, -1)),
                         (1, HoleTile(None, None, None),  0, True, (-1, -1)),
                        ])
def test_robot_died(lives_before, tile, lives_after, active, coordinates):
    """
    When robot comes to a HoleTile (or goes / is pushed out of the game board),
    he gets killed.
    Check that his lives were lowered, he got inactive till the next game round
    and his coordinates changed to the (-1, -1).
    """
    robot = Robot(Direction.N, None, None, (0, 0))
    state = State({(0, 1): [tile]}, [robot], 1)
    robot.lives = lives_before
    robot.walk(1, state)
    assert robot.lives == lives_after
    assert robot.inactive == active
    assert robot.coordinates == coordinates


# FlagTile

@pytest.mark.parametrize(("flags_before", "tile", "flags_after", "start_coordinates_after"),
                        [(3, FlagTile(None, None, [{'value': 1}]),  3,  (1, 1)),
                         (3, FlagTile(None, None, [{'value': 4}]),  4, (0, 0)),
                         (3, FlagTile(None, None, [{'value': 5}]),  3, (1, 1)),
                        ])
def test_robot_collected_flags(flags_before, tile, flags_after, start_coordinates_after):
    """
    When a robot stands on FlagTile with appropriate number (+1 to his current flag count), he collects it.
    He doesn't collect the flags with the other number than defined.    They don't have any effect on him.
    With the flag collected the starting coordinates change to the tile's coordinates.
    """
    robot = Robot(None, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], 1)
    robot.flags = flags_before
    robot.start_coordinates = (1, 1)
    apply_tile_effects(state)
    assert robot.flags == flags_after
    assert robot.start_coordinates == start_coordinates_after


# WallTile

@pytest.mark.parametrize(("input_coordinates", "output_coordinates"),
                        [((0, 0), (0, 0)),
                         ((1, 0), (1, 0)),
                         ((2, 0), (2, 1)),
                         ((3, 0), (3, 1)),
                         ])
def test_robot_is_stopped_by_wall(input_coordinates, output_coordinates):
    """
    Take robot's coordinates, move's direction and distance and assert robot
    was moved to correct coordinates.
    """
    board = get_board("maps/test_walls.json")
    robot = Robot(None, None, None, input_coordinates)
    state = State(board, [robot], 25)
    robot.move(Direction.N, 2, state)
    assert robot.coordinates == output_coordinates


# LaserTile
@pytest.mark.parametrize(("input_coordinates", "output_damages"),
                        [((1, 2), 4),
                         ((3, 1), 4),
                         ((2, 1), 4),
                         ((0, 1), 6),
                         ((3, 3), 8),
                         ((2, 3), 7),
                         ])
def test_robot_is_damaged_by_laser(input_coordinates, output_damages):
    """
    When robot stands on laser tile, he is damaged according to the laser strength, but only if there is no obstacle in the way.
    If there are obstacles, damage count changes accordingly.

    TODO: currently in backend.py robot is initialized with 4 damages.
    When it is changed back to 0 damages, the values must be changed in the test as well.
    """
    board = get_board("maps/test_laser.json")
    robot_obstacle1 = Robot(Direction.N, None, None, (1, 1))
    robot_obstacle2 = Robot(Direction.N, None, None, (3, 2))
    robot = Robot(Direction.E, None, None, input_coordinates)
    state = State(board, [robot_obstacle1, robot_obstacle2, robot], 16)
    apply_tile_effects(state)
    assert robot.damages == output_damages





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
