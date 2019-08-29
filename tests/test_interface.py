from interface import InterfaceState


def test_init():
    """
    Smoke test just to initialize empty interface state.
    """
    interface_state = InterfaceState()
    assert interface_state.robot is None
    assert len(interface_state.my_program) == 5


def test_as_dict():
    """
    Assert the correct data are transformed into dictionary.
    """
    interface_state = InterfaceState()
    interface_state.my_program = "ABC"
    interface_state.power_down = True
    interface_state.confirmed = False
    interface_state.my_game_round = 128

    transformed = interface_state.as_dict()
    assert transformed["interface_data"]["my_program"] == "ABC"
    assert transformed["interface_data"]["power_down"] is True
    assert transformed["interface_data"]["confirmed"] is False
    assert transformed["interface_data"]["my_game_round"] == 128


def start_interface_state():
    """
    Initialize almost empty interface for the other tests.
    """
    interface_state = InterfaceState()
    interface_state.dealt_cards = ["A", "B", "C", "D"]
    return interface_state


def test_non_existing_card_cannot_be_chosen():
    """
    Have 4 cards on hand, try to choose 6th card. Assert None is returned.
    """
    interface_state = start_interface_state()
    assert interface_state.select_card(6) is None


def test_if_selection_confirmed_card_cannot_be_chosen():
    """
    When selection is confirmed, no card can be chosen.
    Assert None is returned.
    """
    interface_state = start_interface_state()
    interface_state.selection_confirmed = True
    assert interface_state.select_card(2) is None


def test_cursor_moves_when_card_is_chosen():
    """
    When card is chosen, its index is added to my_program.
    Cursor moves to the next position (+1) if it is possible.
    """
    interface_state = start_interface_state()
    interface_state.cursor_index = 3
    interface_state.select_card(2)
    assert interface_state.my_program[3] == 2
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
    assert interface_state.my_program[2] is None
    assert interface_state.cursor_index == 2


def test_cursor_is_not_moving_when_at_the_last_position():
    """
    When card is chosen, its index is added to my_program.
    Cursor can't move to another position so it stays at the last position.
    """
    interface_state = start_interface_state()
    interface_state.cursor_index = 4
    interface_state.select_card(2)
    assert interface_state.my_program[4] == 2
    assert interface_state.cursor_index == 4
