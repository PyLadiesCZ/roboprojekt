"""
Use the test maps to test particular tiles effects.
Read commands from yaml file located in the same directory as test map,
and convert them into robot's program.
Play the game with given cards, apply tile's effects and compare the result
with the expected one.
This file works with maps located in tests/.

TODO: decoding the expected results.
"""

from pathlib import Path

import pytest
import yaml

from backend import get_start_state, get_start_tiles, apply_all_effects
from backend import MovementCard, RotationCard

CARD_TYPES = {
    "move": MovementCard,
    "rotate": RotationCard,
}


def get_paths_to_maps_and_commands():
    """
    Go through all 'tests/' folders and create tuples with paths to test files
    (map.json, commands.yaml).
    Return the list of test file sets.
    """
    paths_to_maps_with_commands = []
    source_path = Path("tests/")
    for path in source_path.glob("test_*"):
        if path.is_dir():
            commands = None
            for file in path.iterdir():
                if file.name == "map.json":
                    map = file
                if file.name == "commands.yaml":
                    commands = file
            paths_to_maps_with_commands.append((map, commands))
    return paths_to_maps_with_commands


def read_commands(file):
    """
    Load the file with yaml commands for robots.
    """

    with open(file) as commands_file:
        return yaml.safe_load(commands_file)


def get_cards_from_commands(commands):
    """
    Decode the first part of yaml command - actions.
    Transform actions to robot's program
    (list of cards assigned to 1st, 2nd, etc. robots).
    """
    try:
        actions = commands['actions']

    except TypeError:
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


def get_registers(commands):
    """
    Return the count of registers for test game.
    Look at actions section and check the length of first set of cards.
    If there are no actions (ergo we test only tile effects),
    number of registers is 1.
    """

    try:
        registers = len(commands["actions"][0])
    except TypeError:
        registers = 1
    return registers


def decode_results():
    """
    Decode the results that are not visible on the map, eg. robot's damages,
    lives, flags.
    Use for comparing the expected state of game with the given one.
    """
    pass


def assign_cards_to_robots(all_cards, state):
    """
    Take cards read from external file and
    assign them to the robots as their program.
    """
    for cards_set, robot in zip(all_cards, state.robots):
        robot.program = cards_set


@pytest.mark.parametrize(
        ("map_file", "commands_file"),
        get_paths_to_maps_and_commands(),
        )
def test_play_game(map_file, commands_file):
    """
    Play the game with given map.
    """

    commands = read_commands(commands_file)
    state = get_start_state(map_file)

    all_cards = get_cards_from_commands(commands)
    if all_cards:
        assign_cards_to_robots(all_cards, state)

    apply_all_effects(state, registers=get_registers(commands))

    stop_fields = get_start_tiles(state._board, "stop")

    for robot in state.robots:
        assert robot.coordinates == stop_fields[(state.robots.index(robot) + 1)]["coordinates"]
        assert robot.direction == stop_fields[(state.robots.index(robot) + 1)]["tile_direction"]
