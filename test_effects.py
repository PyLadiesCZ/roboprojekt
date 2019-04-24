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

def get_my_robots():
    state = get_start_state("tests/test_gear/map.json", "start")

    print(state)

    state2 = get_start_state("tests/test_gear/map.json", "stop")

    print(state2)
