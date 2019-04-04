import pytest
from pathlib import Path

from backend import create_robots, get_start_state, Robot, State, MovementCard, RotationCard, apply_tile_effects
from util import Direction, Rotation
from tile import Tile, HoleTile, GearTile, PusherTile, RepairTile, FlagTile
from loading import get_board


def test_robots_on_start_coordinates():
    """
    Assert that the result of create_robots is a list which contains
    Robot objects with correct attribute coordinates.
    """
    board = get_board("maps/test_3.json")
    robots = create_robots(board)
    assert isinstance(robots, list)
    assert isinstance(robots[0], Robot)


def test_start_state():
    """
    Assert that created start state (board and robots) contains
    the correct instances of objects.
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


def test_robot_and_tiles_shoot():
    """
    Robots are placed on a test_laser.json map.
    There are some walls that stop their lasers on the way.
    (In order to see the "human" version with arrows representing robots,
    check test_shoot_human_view.json),
    They should receive damages according to their and lasers' position.
    """
    board = get_board("maps/test_laser.json")

    robots = [Robot(Direction.W, None, None, (2, 2)),
              Robot(Direction.N, None, None, (1, 1)),
              Robot(Direction.E, None, None, (0, 2)),
              Robot(Direction.W, None, None, (1, 2)),
              Robot(Direction.S, None, None, (1, 3)),
              Robot(Direction.E, None, None, (0, 0)),
              Robot(Direction.N, None, None, (2, 0)),
              Robot(Direction.E, None, None, (3, 0)),
              Robot(Direction.N, None, None, (2, 1)),
              Robot(Direction.S, None, None, (3, 3)),
              ]
    for robot in robots:
        robot.damages = 0

    state = State(board, robots, (4, 4))
    apply_tile_effects(state)
    damages_list = [0, 4, 0, 2, 0, 0, 1, 1, 1, 4]

    for robot in robots:
        assert robot.damages == damages_list[robots.index(robot)]


def test_power_down_robots_dont_shoot():
    """
    Robots are placed on a test_laser.json map.
    There are some walls that stop their lasers on the way.
    (In order to see the "human" version with arrows representing robots,
    check test_shoot_human_view.json),
    They shouldn't receive damage when they are under power-down.
    """
    board = get_board("maps/test_laser.json")

    robots = [Robot(Direction.W, None, None, (2, 2)),
              Robot(Direction.N, None, None, (1, 1)),
              Robot(Direction.E, None, None, (0, 2)),
              Robot(Direction.W, None, None, (1, 2)),
              Robot(Direction.S, None, None, (1, 3)),
              Robot(Direction.E, None, None, (0, 0)),
              Robot(Direction.N, None, None, (2, 0)),
              Robot(Direction.E, None, None, (3, 0)),
              Robot(Direction.N, None, None, (2, 1)),
              Robot(Direction.S, None, None, (3, 3)),
              ]
    for robot in robots:
        robot.damages = 0
        robot.power_down = True

    state = State(board, robots, (4, 4))
    apply_tile_effects(state)
    damages_list = [0, 4, 0, 0, 0, 0, 0, 0, 0, 4]

    for robot in robots:
        assert robot.damages == damages_list[robots.index(robot)]



# RepairTile

@pytest.mark.parametrize(("damages_before", "tile", "damages_after"),
                         [(0, RepairTile(None, None, [{'value': True}]), 0),
                         (9, RepairTile(None, None, [{'value': True}]), 8),
                         (3, RepairTile(None, None, [{'value': True}]), 2),
                          ])
def test_robot_is_repaired_after_5th_round(damages_before, tile, damages_after):
    """
    When robot is on RepairTile he is supposed to be repaired after the 5th register.
    If he doesn't have any damages, the count remains the same as previous.
    """
    robot = Robot(Direction.N, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], (1, 1))
    robot.damages = damages_before
    state.register = 5
    apply_tile_effects(state)
    assert robot.damages == damages_after


@pytest.mark.parametrize(("damages", "tile", "current_register"),
                         [(0, RepairTile(None, None, [{'value': True}]), 1),
                         (9, RepairTile(None, None, [{'value': True}]), 2),
                         (3, RepairTile(None, None, [{'value': True}]), 3),
                         (5, RepairTile(None, None, [{'value': True}]), 4),
                          ])
def test_robot_is_not_repaired(damages, tile, current_register):
    """
    When robot is on RepairTile but the register phase is not 5, he is not yet repaired. His damage count doesn't change.
    """
    robot = Robot(Direction.N, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], (1, 1))
    robot.damages = damages
    state.register = current_register
    apply_tile_effects(state)
    assert robot.damages == damages


@pytest.mark.parametrize(("tile", "coordinates_after"),
                         [(RepairTile(None, None, [{'value': True}]), (0, 0)),
                         (RepairTile(None, None, [{'value': False}]), (1, 1)),
                          ])
def test_robot_changed_start_coordinates(tile, coordinates_after):
    """
    When robot is on RepairTile with special property, he changes his start coordinates to the tile coordinates.
    On a normal RepairTile he doesn't change the start tile.
    """
    robot = Robot(Direction.N, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], (1, 1))
    robot.start_coordinates = (1, 1)
    apply_tile_effects(state)
    assert robot.start_coordinates == coordinates_after


# GearTile

@pytest.mark.parametrize(("direction_before", "tile", "direction_after"),
                         [(Direction.E, GearTile(None, None, [{'value': -1}]),  Direction.N),
                         (Direction.E, GearTile(None, None, [{'value': 1}]), Direction.S),
                         (Direction.S, GearTile(None, None, [{'value': -1}]), Direction.E),
                         (Direction.S, GearTile(None, None, [{'value': 1}]), Direction.W),
                          ])
def test_robot_changed_direction(direction_before, tile, direction_after):
    """
    When robot is on GearTile, he should be rotated according to the direction of the tile.
    Check that his direction changed after applying tile effect.
    """
    robot = Robot(direction_before, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], (1, 1))
    apply_tile_effects(state)
    assert robot.direction == direction_after


# HoleTile hidden in walk method

@pytest.mark.parametrize(("lives_before", "lives_after"),
                         [(3, 2),
                         (2, 1),
                         (1, 0),
                          ])
def test_robot_died(lives_before, lives_after):
    """
    When robot comes to a HoleTile (or goes / is pushed out of the game board),
    he gets killed.
    Check that his lives were lowered, he got inactive till the next game round
    and his coordinates changed to the None.
    """
    robot = Robot(Direction.N, None, None, (0, 0))
    state = State({(0, 1): [HoleTile(None, None, None)]}, [robot], (1, 2))
    robot.lives = lives_before
    robot.walk(1, state)
    assert robot.lives == lives_after
    assert robot.inactive is True
    assert robot.coordinates == None


# FlagTile

@pytest.mark.parametrize(("flags_before", "tile", "flags_after"),
                         [(3, FlagTile(None, None, [{'value': 1}]),  3),
                         (3, FlagTile(None, None, [{'value': 4}]),  4),
                         (3, FlagTile(None, None, [{'value': 5}]),  3),
                          ])
def test_robot_collected_flags(flags_before, tile, flags_after):
    """
    When a robot stands on FlagTile with appropriate number (+1 to his current flag count), he collects it.
    He doesn't collect the flags with the other number than defined. They don't have any effect on him.
    """
    robot = Robot(Direction.N, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], (1, 1))
    robot.flags = flags_before
    apply_tile_effects(state)
    assert robot.flags == flags_after


@pytest.mark.parametrize(("tile"),
                         [(FlagTile(None, None, [{'value': 1}])),
                         (FlagTile(None, None, [{'value': 4}])),
                         (FlagTile(None, None, [{'value': 5}])),
                          ])
def test_robot_changed_coordinates(tile):
    """
    When a robot stands on FlagTile the start coordinates change to the tile's coordinates.
    """
    robot = Robot(Direction.N, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], (1, 1))
    robot.start_coordinates = (1, 1)
    apply_tile_effects(state)
    assert robot.start_coordinates == (0, 0)


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
    A special map test_walls was created in order to test this feature.
    """
    board = get_board("maps/test_walls.json")
    robot = Robot(Direction.N, None, None, input_coordinates)
    state = State(board, [robot], (5, 5))
    robot.move(Direction.N, 2, state)
    assert robot.coordinates == output_coordinates


# LaserTile

@pytest.mark.parametrize(("input_coordinates", "damages_after"),
                         [((1, 2), 0),
                         ((3, 1), 0),
                         ((2, 1), 0),
                         ((0, 1), 2),
                         ((3, 3), 4),
                         ((2, 3), 3),
                          ])
def test_robot_is_damaged_by_laser(input_coordinates, damages_after):
    """
    When robot stands on laser tile, he is damaged according to the laser strength,
    but only if there is no obstacle in the way.
    If there are obstacles, damage count changes accordingly.
    A special map test_laser was created in order to test this feature.
    """
    board = get_board("maps/test_laser.json")
    robot_obstacle1 = Robot(Direction.S, None, None, (1, 1))
    robot_obstacle2 = Robot(Direction.E, None, None, (3, 2))
    robot = Robot(Direction.W, None, None, input_coordinates)
    robot.damages = 0
    state = State(board, [robot_obstacle1, robot_obstacle2, robot], (4, 4))
    apply_tile_effects(state)
    assert robot.damages == damages_after


# PusherTile

@pytest.mark.parametrize(("register", "tile", "output_coordinates"),
                         [(1, PusherTile(Direction.N, None, [{'value': 1}]), (1, 0)),
                         (2, PusherTile(Direction.N, None, [{'value': 1}]), (1, 1)),
                         (3, PusherTile(Direction.N, None, [{'value': 0}]), (1, 1)),
                         (4, PusherTile(Direction.N, None, [{'value': 0}]), (1, 0)),
                         (5, PusherTile(Direction.N, None, [{'value': 1}]), (1, 0)),
                          ])
def test_robot_is_pushed_at_the_correct_round(register, tile, output_coordinates):
    """
    When robot is standing on a PusherTile, he should be pushed in the direction of pusher's force.
    Eg. pusher on the North tile side forces the robot's movement to the South.
    Robot's direction doesn't change, just the coordinates.
    The push is performed only at the certain register (1-3-5 or 2-4) according
    to the value on the tile.
    """
    robot = Robot(Direction.W, None, None, (1, 1))
    state = State({(1, 0): [Tile(None, None, None)], (1, 1): [tile]}, [robot], (2, 1))
    state.register = register
    apply_tile_effects(state)
    assert robot.direction == Direction.W
    assert robot.coordinates == output_coordinates


@pytest.mark.parametrize(("tile", "output_coordinates"),
                         [(PusherTile(Direction.N, None, [{'value': 1}]), (1, 0)),
                         (PusherTile(Direction.S, None, [{'value': 1}]), (1, 2)),
                         (PusherTile(Direction.E, None, [{'value': 1}]), (0, 1)),
                         (PusherTile(Direction.W, None, [{'value': 1}]), (2, 1)),
                          ])
def test_robot_is_pushed_to_the_correct_direction(tile, output_coordinates):
    """
    When robot is standing on a PusherTile, he should be pushed in the direction of pusher's force.
    Eg. pusher on the North tile side forces the robot's movement to the South.
    Robot's direction doesn't change, just the coordinates.
    The test asserts the coordinates change to a correct ones (in a correct direction).
    """
    robot = Robot(Direction.S, None, None, (1, 1))
    state = State({(1, 0): [Tile(None, None, None)], (0, 1): [Tile(None, None, None)], (2, 1): [Tile(None, None, None)], (1, 2): [Tile(None, None, None)], (1, 1): [tile]}, [robot], (3, 3))
    state.register = 1
    apply_tile_effects(state)
    assert robot.direction == Direction.S
    assert robot.coordinates == output_coordinates


@pytest.mark.parametrize(("tile"),
                         [(PusherTile(Direction.N, None, [{'value': 1}])),
                         (PusherTile(Direction.S, None, [{'value': 1}])),
                         (PusherTile(Direction.E, None, [{'value': 1}])),
                         (PusherTile(Direction.W, None, [{'value': 1}])),
                          ])
def test_robot_is_pushed_out_of_the_board(tile):
    """
    When robot is standing on a PusherTile, he should be pushed in the direction of pusher's force.
    Eg. pusher on the North tile side forces the robot's movement to the South.
    If he is pushed out of a board game, he should be killed.
    The test asserts the attributes: coordinates, lives and inactive change.
    """
    robot = Robot(Direction.S, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], (1, 1))
    state.register = 1
    apply_tile_effects(state)
    assert robot.lives == 2
    assert robot.inactive is True
    assert robot.coordinates is None


def test_robot_on_start_has_the_correct_direction():
    """
    When robot is created, his direction shoud be the same as the direction
    of start tile he stands on.
    Assert the direction is correcly initiated.
    """
    state = get_start_state("maps/test_start_direction.json")
    for robot in state.robots:
        tile_direction = state.get_tiles(robot.coordinates)[0].direction
        assert robot.direction == tile_direction


@pytest.mark.parametrize(("robot_index", "expected_coordinates"),
                         [(0, (0, 0)),
                          (1, (1, 0)),
                          (2, (2, 0)),
                          (3, (3, 0)),
                          ])
def test_robots_order_on_start(robot_index, expected_coordinates):
    """
    The order of robots list should reflect their starting positions.
    First robot from the list stands on first start tile and so on.
    Assert the list is correcly created.
    Test to check the behaviour in Python 3.5.
    """
    state = get_start_state("maps/test_start_direction.json")
    current_robot = state.robots[robot_index]
    assert current_robot.coordinates == expected_coordinates



@pytest.mark.parametrize(("direction", "card", "new_coordinates"),
                         [(Direction.E, MovementCard(100, 1), (5, 7)),
                         (Direction.E, MovementCard(100, 2), (6, 7)),
                         (Direction.E, MovementCard(100, 3), (7, 7)),
                         (Direction.E, MovementCard(100, -1), (3, 7)),
                         (Direction.S, MovementCard(100, 1), (4, 6)),
                         (Direction.S, MovementCard(100, 2), (4, 5)),
                         (Direction.S, MovementCard(100, 3), (4, 4)),
                         (Direction.S, MovementCard(100, -1), (4, 8)),
                         (Direction.N, MovementCard(100, -1), (4, 6)), (Direction.W, MovementCard(100, -1), (5, 7)),
                          ])
def test_move_cards(direction, card, new_coordinates):
    """
    Give mock robot the MovementCard and check if he moved to the expected coordinates.
    Check if the robot's direction remained the same.
    """
    robot = Robot(direction, None, None, (4, 7))
    robot.program = [card]
    state = get_start_state("maps/test_3.json")
    robot.apply_card_effect(state)
    assert robot.coordinates == new_coordinates
    assert robot.direction == direction


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
