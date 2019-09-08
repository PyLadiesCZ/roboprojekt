import pytest
from interface import InterfaceState


def test_init():
    """
    Smoke test just to initialize empty interface state.
    """
    interface_state = InterfaceState(change_callback=test_print)
    assert interface_state.robot is None
    assert len(interface_state.program) == 5


def test_as_dict():
    """
    Assert the correct data are transformed into dictionary.
    """
    interface_state = InterfaceState(change_callback=test_print)
    interface_state.program = "ABC"
    interface_state.power_down = True
    interface_state.confirmed = False
    interface_state.game_round = 128

    transformed = interface_state.as_dict()
    assert transformed["interface_data"]["program"] == "ABC"
    assert transformed["interface_data"]["power_down"] is True
    assert transformed["interface_data"]["confirmed"] is False
    assert transformed["interface_data"]["game_round"] == 128


def start_interface_state(confirmed=False, program=False):
    """
    Initialize almost empty interface for the other tests.
    """
    interface_state = InterfaceState(change_callback=test_print)
    interface_state.dealt_cards = ["A", "B", "C", "D"]
    if confirmed:
        interface_state.selection_confirmed = True
    if program:
        interface_state.program = [4, 3, 2, 1]
    return interface_state


def test_non_existing_card_cannot_be_chosen():
    """
    Have 4 cards on hand, try to choose 6th card. Assert no card was chosen.
    """
    interface_state = start_interface_state()
    interface_state.select_card(6)
    assert interface_state.program == [None, None, None, None, None]


def test_if_selection_confirmed_card_cannot_be_chosen():
    """
    When selection is confirmed, no card can be chosen.
    Assert program hasn't changed
    """
    interface_state = start_interface_state(confirmed=True)
    interface_state.select_card(2)
    assert interface_state.program == [None, None, None, None, None]


def test_cursor_moves_when_card_is_chosen():
    """
    When card is chosen, its index is added to program.
    Cursor moves to the next position (+1) if it is possible.
    """
    interface_state = start_interface_state()
    interface_state.cursor_index = 3
    interface_state.select_card(2)
    assert interface_state.program[3] == 2
    assert interface_state.cursor_index == 4


def test_cursor_not_moving_card_is_not_chosen():
    """
    When card is already chosen once, it is impossible to choose it again.
    Cursor doesn't move to the next position.
    """
    interface_state = start_interface_state()
    interface_state.select_card(2)
    interface_state.cursor_index = 2
    interface_state.select_card(2)
    assert interface_state.program[2] is None
    assert interface_state.cursor_index == 2


def test_cursor_is_not_moving_when_at_the_last_position():
    """
    When card is chosen, its index is added to program.
    Cursor can't move to another position so it stays at the last position.
    """
    interface_state = start_interface_state()
    interface_state.cursor_index = 4
    interface_state.select_card(2)
    assert interface_state.program[4] == 2
    assert interface_state.cursor_index == 4


def test_return_card_when_selection_not_confirmed():
    """
    If selection is not confirmed,
    it is possible to return card on which there is cursor.
    """
    interface_state = start_interface_state(program=True)
    interface_state.return_card()
    interface_state.cursor_index = 2
    interface_state.return_card()
    assert interface_state.program == [None, 3, None, 1]


def test_return_card_when_selection_confirmed_():
    """
    If selection is confirmed,
    it is not possible to return any card.
    """
    interface_state = start_interface_state(confirmed=True, program=True)
    interface_state.cursor_index = 3
    interface_state.return_card()
    assert interface_state.program == [4, 3, 2, 1]


def test_return_cards_when_selection_confirmed():
    """
    If selection is confirmed,
    it is not possible to return all card.
    """
    interface_state = start_interface_state(confirmed=True, program=True)
    interface_state.blocked_cards = ["D"]
    interface_state.return_cards()
    assert interface_state.program == [4, 3, 2, 1]


def test_return_cards_when_selection_not_confirmed():
    """
    If selection is not confirmed,
    it is possible to return all cards -
    blocked cards aren´t in program.
    """
    interface_state = start_interface_state(program=True)
    interface_state.blocked_cards = ["D"]
    interface_state.return_cards()
    assert interface_state.program == [None, None, None, None]


def test_return_cards_when_selection_not_confirmed_2():
    """
    If selection is not confirmed,
    it is possible to return all cards.
    """
    interface_state = start_interface_state(program=True)
    interface_state.return_cards()
    assert interface_state.program == [None, None, None, None]


def test_cursor_is_not_moving_when_at_the_first_position():
    """
    If selection is not confirmed and cursor is on the first position,
    it is not possible to move it to the left.
    """
    interface_state = start_interface_state(program=True)
    interface_state.cursor_index_minus()
    assert interface_state.cursor_index == 0


def test_cursor_is_moving_to_the_left():
    """
    If selection is not confirmed and cursor is not on the first position,
    it is possible to move it to the left.
    """
    interface_state = start_interface_state(program=True)
    interface_state.cursor_index = 3
    interface_state.cursor_index_minus()
    assert interface_state.cursor_index == 2


def test_power_down_cannot_be_switched():
    """
    If selection is confirmed, power down can't be switched on or off.
    """
    interface_state = start_interface_state(program=True)
    interface_state.confirm_selection()
    interface_state.switch_power_down()
    assert interface_state.power_down is False


@pytest.mark.parametrize(
    ("current_value", "expected_value"), [(True, False), (False, True)]
)
def test_power_down_can_be_switched(current_value, expected_value):
    """
    If selection is not confirmed, power down can be switched on and off.
    """
    interface_state = start_interface_state()
    interface_state.power_down = current_value
    interface_state.switch_power_down()
    assert interface_state.power_down is expected_value


def test_change_callback(capsys):
    """
    Test if change_callback function works and assert correct result.
    Test function "sum" is used.
    """
    interface_state = start_interface_state(test_print)
    print("Hello")
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"


def test_print():
    """
    Test function which is used as change_callback function for testing.
    """
    print("Hello")
