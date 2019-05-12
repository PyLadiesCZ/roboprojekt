"""
Use the test maps to test particular tiles effects.
Read commands from yaml file located in the same directory as test map,
and convert them into robot's program.
Play the game with given cards, apply tile's effects and compare the result
with the expected one.
TODO: decoding the expected results.
TODO: better handling what map is being tested now.
This file works currently with maps from tests/. Under heavy construction.
"""

from pathlib import Path

import pytest
import yaml

from backend import get_start_state, get_start_tiles, apply_all_effects
from backend import MovementCard, RotationCard
from tile import StartTile


CARD_TYPES = {
    "move": MovementCard,
    "rotate": RotationCard,
}


def get_test_maps():
    test_maps_with_commands = []
    source_path = Path("tests/")
    for path in source_path.glob("test_*"):
        if path.is_dir():
            commands = None
            for file in path.iterdir():
                if file.name == "map.json":
                    map = file
                if file.name == "commands.yaml":
                    commands = file
            test_maps_with_commands.append((map, commands))
    return test_maps_with_commands


def get_commands(file):
    """
    Open the file with yaml commands for robots.
    Currently opens only one file.
    """
    try:
        with open(file) as commands_file:
            return yaml.safe_load(commands_file)
    except TypeError:
        file = None


def get_test_cards(commands):
    """
    Decode the first part of yaml command - actions.
    Transform actions to robot's program
    (list of cards assigned to 1st, 2nd, etc. robots).
    """
    try:
        yaml_actions = commands['actions']

    except KeyError:
        robots_program = None

    else:
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

def get_registers(commands):
    return commands['registers']


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
                robot._serial_number = tile.number


def match_programs_to_robots(robots_program, state):
    """
    Take cards read from external file and match them to the robots as their program.
    """
    for robot_number, robot_cards in robots_program.items():
        for robot in state.robots:
            if robot._serial_number == robot_number:
                robot.program = robot_cards


def test_play_test_game():
    """
    Play the game with given map.
    """

    for map, commands in get_test_maps():
        read_commands = get_commands(commands)
        state = get_start_state(map)
        print("File with map:", map)
        add_start_tile_number_to_robots(state)

        robots_program = get_test_cards(read_commands)
        if robots_program:
            match_programs_to_robots(robots_program, state)

        apply_all_effects(state, registers=get_registers(read_commands))

        stop_fields = get_start_tiles(state._board, "stop")

        for robot in state.get_active_robots():
            assert robot.coordinates == stop_fields[robot._serial_number]["coordinates"]
            assert robot.direction == stop_fields[robot._serial_number]["tile_direction"]
