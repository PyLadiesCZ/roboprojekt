import pytest
import yaml


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
