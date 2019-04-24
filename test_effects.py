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
