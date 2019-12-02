"""
Use the test maps to test particular tiles effects.
Read commands from yaml file located in the same directory as test map,
and convert them into robot's program. (The commands are not mandatory,
if you want to test only the tile effects).
Play the game with given cards, apply tile's effects and compare the result
with the expected one.
You can compare: coordinates and direction (drawn on map with stop tiles),
as well as hidden attributes: flags, damages, lives, power_down,
start_coordinates - they must be listed in commands file as prerequisites
(initial setup) and results (to compare with).
This file works with maps located in tests/.
"""

from pathlib import Path

import pytest
import yaml

from backend import State, get_start_tiles
from backend import MovementCard, RotationCard

CARD_TYPES = {
    "move": MovementCard,
    "rotate": RotationCard,
}


def get_test_names():
    """
    Go through all 'tests/' folders and get their names.
    Yield the next folder name.
    """
    source_path = Path("tests/")
    for path in source_path.glob("test_*"):
        if path.is_dir():
            yield path.name


def read_commands(file):
    """
    Load the file with yaml commands for robots.
    """
    try:
        with open(file) as commands_file:
            file = yaml.safe_load(commands_file)
    except TypeError:
        file = {}
    return file


def get_registers(commands):
    """
    Return the count of registers for test game.
    Look at actions section and check the length of first set of cards.
    If there are no actions (ergo we test only tile effects),
    number of registers is 1.
    """
    actions = commands.get("actions", [[1]])
    registers = len(actions[0])
    return registers


def get_cards_from_commands(commands):
    """
    Decode the first part of yaml command - actions.
    Transform actions to robot's program
    (list of cards assigned to 1st, 2nd, etc. robots).
    """
    try:
        actions = commands['actions']

    except KeyError:
        all_cards = None

    else:
        all_cards = []

        for actions_set in actions:
            cards_set = []
            for card in actions_set:
                # Create the correct Card instance with read properties.
                one_card = CARD_TYPES[card["type"]](
                    card["priority"],
                    card["value"],
                    )
                cards_set.append(one_card)
            all_cards.append(cards_set)
    return all_cards


def assign_cards_to_robots(commands, state):
    """
    Take cards read from external file and
    assign them to the robots as their program.
    """
    if commands:
        all_cards = get_cards_from_commands(commands)
        if all_cards:
            for cards_set, robot in zip(all_cards, state.robots):
                robot.program = cards_set


def assign_prerequisites_to_robots(commands, state):
    """
    Take values for start state read from external file and
    assign them to the robots as their attributes.
    """
    if commands:
        prerequisites = commands.get('prerequisites', None)
        if prerequisites:
            for attribute, robot in zip(prerequisites, state.robots):
                print("attribute", attribute)
                if "damages" in attribute:
                    robot.damages = attribute["damages"]
                if "flags" in attribute:
                    robot.flags = attribute["flags"]
                if "lives" in attribute:
                    robot.lives = attribute["lives"]
                if "power_down" in attribute:
                    robot.power_down = attribute["power_down"]


def compare_results_with_robots(commands, state):
    """
    Take results read from external file and compare the values
    with the values of robots attributes.
    """
    if commands:
        results = commands.get("results", None)
        if results:
            print(results)
            for attribute, robot in zip(results, state.robots):
                if "damages" in attribute:
                    assert robot.damages == attribute["damages"]
                if "flags" in attribute:
                    assert robot.flags == attribute["flags"]
                if "lives" in attribute:
                    assert robot.lives == attribute["lives"]
                if "power_down" in attribute:
                    assert robot.power_down == attribute["power_down"]
                if "start" in attribute:
                    start_coordinates = []
                    for coordinates in attribute["start"]:
                        start_coordinates.append(tuple(coordinates))
                    assert robot.start_coordinates == start_coordinates


@pytest.mark.parametrize(
        ("test_name"),
        get_test_names(),
        )
def test_play_game(test_name):
    """
    Play the game with given map.
    """
    map_file = Path("tests/") / test_name / "map.json"
    commands_file = Path("tests/") / test_name / "commands.yaml"
    if not commands_file.exists():
        commands_file = None

    state = State.get_start_state(map_file)
    stop_fields = get_start_tiles(state._board, "stop")

    commands = read_commands(commands_file)

    assign_cards_to_robots(commands, state)
    assign_prerequisites_to_robots(commands, state)

    # Leave it here for debugging purpose :)
    # for robot in state.robots:
    #     print(robot.program)
    #     print(robot.damages)
    #     print(robot.flags)
    #     print(robot.lives)
    #     print(robot.power_down)
    #     print(robot.start_coordinates)

    state.apply_all_effects(registers=get_registers(commands))
    compare_results_with_robots(commands, state)

    # for robot in state.robots:
    #     print(robot.program)
    #     print(robot.damages)
    #     print(robot.flags)
    #     print(robot.lives)
    #     print(robot.power_down)
    #     print(robot.start_coordinates)

    for robot in state.robots:
        robot_field = state.robots.index(robot) + 1
        assert robot.coordinates == stop_fields[robot_field]["coordinates"]
        assert robot.direction == stop_fields[robot_field]["tile_direction"]
