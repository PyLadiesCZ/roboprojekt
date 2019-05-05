"""
Use the test maps to test particular tiles effects.
Read commands from yaml file located in the same directory as test map,
and convert them into robot's program.
Play the game with given cards, apply tile's effects and compare the result
with the expected one.
TODO: decoding the expected results.
TODO: reading files from different directories.
This file works currently only with one map. Under heavy construction.
"""

import pytest
import yaml

from backend import get_start_state, get_start_tiles, play_the_game
from backend import MovementCard, RotationCard
from tile import StartTile


CARD_TYPES = {
    "move": MovementCard,
    "rotate": RotationCard,
}


def get_commands(adr):
    """
    Open the file with yaml commands for robots.
    Currently opens only one file.
    """
    with open(adr) as commands_file:
        return yaml.safe_load(commands_file)


def get_test_cards(commands):
    """
    Decode the first part of yaml command - actions.
    Transform actions to robot's program
    (list of cards assigned to 1st, 2nd, etc. robots).
    """

    yaml_actions = commands['actions']

    # Create dictionary: for every robot empty list to be filled with cards
    robots_program = {robot_number: [] for robot_number in yaml_actions.keys()}

    for robot_number, actions in yaml_actions.items():
        robot_cards = robots_program[robot_number]

        for action in actions:

            # Create the correct Card instance with read properties.
            # Add the card to robot_actions list and assign the list to the key.
            robot_card = CARD_TYPES[action["type"]](
                action["priority"],
                action["value"],
                )

            robot_cards.append(robot_card)
            robots_program[robot_number] = robot_cards

    return robots_program


def decode_results():
    """
    Decode the results that are not visible on the map, eg. robot's damages,
    lives, flags.
    Use for comparing the expected state of game with the given one.
    """
    pass


def add_start_tile_number_to_robots(state):
    """
    Add start tile number to robot as an attribute.
    Make it possible to match robot program with robot and compare game states.
    """
    for robot in state.robots:
        for tile in state.get_tiles(robot.coordinates):
            if isinstance(tile, StartTile):
                robot.stn = tile.number


def match_programs_to_robots(robots_program, state):
    """
    Take cards read from external file and match them to the robots as their program.
    """
    for robot_number, robot_cards in robots_program.items():
        for robot in state.robots:
            if robot.stn == robot_number:
                robot.program = robot_cards


def read_commands_and_state():
    commands = get_commands("tests/test_gear/commands.yaml")
    state = get_start_state("tests/test_gear/map.json")
    return commands, state


def play_test_game():
    """
    Play the game with given map.
    """
    commands, state = read_commands_and_state()
    robots_program = get_test_cards(commands)
    add_start_tile_number_to_robots(state)
    match_programs_to_robots(robots_program, state)

    play_the_game(state, rounds=2)

    stop_fields = get_start_tiles(state._board, "stop")

    return state, stop_fields


def test_robots_moved_to_desired_positions():
    """
    Assert the coordinates of robots changed as they were supposed to.
    """
    state, stop_fields = play_test_game()
    for robot in state.get_active_robots():
        assert robot.coordinates == stop_fields[robot.stn]["coordinates"]
