import pytest
import yaml

from backend import get_start_state, get_start_tiles, apply_tile_effects
from backend import MovementCard, RotationCard
from util import Rotation


CARD_TYPES = {
    "move": MovementCard,
    "rotate": RotationCard,
}

ROTATIONS = {
    "left": Rotation.LEFT,
    "right": Rotation.RIGHT,
    "u_turn": Rotation.U_TURN,
}


def get_commands():
    """
    Open the file with yaml commands for robots.
    Currently opens only one file.
    """
    adr = "tests/test_gear/commands.yaml"
    with open(adr) as f:
        data = yaml.safe_load(f)
    return data


def get_test_cards(data):
    """
    Decode the first part of yaml command - actions.
    Transform actions to robot's program
    (list of cards assigned to 1st, 2nd, etc. robots).
    """

    yaml_actions = data['actions']

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


def test_get_my_robots():
    state = get_start_state("tests/test_gear/map.json")
    for robot in state.get_active_robots():
        robot.walk(1, state)
    apply_tile_effects(state)
    for robot in state.get_active_robots():
        robot.walk(1, state)
    print(state)

    stop_pole = get_start_tiles(state._board, "stop")

    print(stop_pole)
    for robot in state.get_active_robots():
        if robot.start_coordinates == (1, 2):
            assert robot.coordinates == stop_pole[1]["coordinates"]
