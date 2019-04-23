from collections import OrderedDict

import pytest
import yaml

from backend import get_start_state


def get_commands():
    adr = "tests/test_gear/commands.yaml"
    with open(adr) as f:
        data = yaml.safe_load(f)
    return data


def get_actions(data):
    actions = data['actions']
    return actions


def decode_actions():
    pass


def decode_results():
    pass


def get_stop_tiles(board):
    """
    Get stop tiles for robots.

    board: dictionary returned by get_board().
    Create an ordered dictionary of all start tiles in the board with start
    tile number as a key and values: coordinates and tile_direction.
    OrderedDict is a structure that ensures the dictionary is stored
    in the order of the new keys being added.
    """

    stop_tiles = {}
    for coordinate, tiles in board.items():
        for tile in tiles:
            if tile.stop_properties_dict(coordinate) is not None:
                stop_tiles[tile.number] = tile.stop_properties_dict(coordinate)

    # Sort created dictionary by the first element - start tile number
    OrderedDict(sorted(stop_tiles.items(), key=lambda stn: stn[0]))

    return stop_tiles


def get_stop_state(map_name):
    """
    Get start state of game.

    map_name: path to map file. Currently works only for .json files from Tiled 1.2
    Create board and robots on start tiles, initialize State object
    containing Tile and Robot object as well as the map size.
    Return State object.
    """
    board = get_board(map_name)
    robots_start = create_robots(board)
    state = State(board, robots_start, tile_count)
    return state


# GearTile
"""
@pytest.mark.parametrize(("direction_before", "tile", "direction_after"),
                         [(Direction.E, GearTile(None, None, [{'value': -1}]),  Direction.N),
                         (Direction.E, GearTile(None, None, [{'value': 1}]), Direction.S),
                         (Direction.S, GearTile(None, None, [{'value': -1}]), Direction.E),
                         (Direction.S, GearTile(None, None, [{'value': 1}]), Direction.W),
                          ])
def test_robot_changed_direction(direction_before, tile, direction_after):

    When robot is on GearTile, he should be rotated according to the direction of the tile.
    Check that his direction changed after applying tile effect.

    robot = Robot(direction_before, None, None, (0, 0))
    state = State({(0, 0): [tile]}, [robot], (1, 1))
    apply_tile_effects(state)
    assert robot.direction == direction_after


def test_robot_on_start_has_the_correct_direction():

    When robot is created, his direction shoud be the same as the direction
    of start tile he stands on.
    Assert the direction is correcly initiated.

    state = get_start_state("tests/test_robot_direction/test_start_direction.json")

    for robot in state.robots:
        tile_direction = state.get_tiles(robot.coordinates)[0].direction
        assert robot.direction == tile_direction


def test_robots_order_on_start():

    The order of robots list should reflect their starting positions.
    First robot from the list stands on first start tile and so on.
    Assert the list is correcly created.

    state = get_start_state("tests/test_robot_direction/test_start_direction.json")

    for robot in state.robots:
        start_tile_number = state.get_tiles(robot.coordinates)[0].number
        assert state.robots.index(robot) + 1 == start_tile_number"""
