class InterfaceState:
    def __init__(self, change_callback):
        self.dealt_cards = []
        self.robot = None
        self.program = [None, None, None, None, None]
        self.blocked_cards = []
        self.power_down = False
        self.selection_confirmed = False
        self.cursor_index = 0  # 0-4 number of positon
        self.timer = None
        # Assign the function that should be called within some InterfaceState methods,
        # eg. after choosing or returning cards on hand,
        # not on change of the purely visual elements of interface, like moving the cursor.
        # Assigned function is be called after every robot-related interface state change.
        self.change_callback = change_callback

    def __repr__(self):
        return f"InterfaceState \
                Cards: {self.dealt_cards}, \
                My Cards: {self.program}, \
                Power Down: {self.power_down,}, \
                Robot: {self.robot}"

    def as_dict(self):
        """
        Return dictionary about state of client_interface."
        """
        return {
            "interface_data": {
                "program": self.program,
                "power_down": self.power_down,
                "confirmed": self.selection_confirmed,
                }
            }

    def select_card(self, dealt_card_index):
        """
        Select a card from the dealt cards and put on
        a place where selector is (in the robot program)
        and selector cursor moves to the next free place.
        """
        if not self.selection_confirmed:
            if dealt_card_index >= len(self.dealt_cards):
                return
            if dealt_card_index not in self.program:
                self.program[self.cursor_index] = dealt_card_index
                self.change_callback()
                # After selecting a card move the cursor to the right
                self.cursor_index_plus()

    def return_card(self):
        """
        Return one selected card from your program back to the dealt cards.
        """
        if not self.selection_confirmed:
            self.program[self.cursor_index] = None
            self.change_callback()

    def return_cards(self):
        """
        Return all cards of your program back to the dealt cards.
        """
        if not self.selection_confirmed:
            for card in range(len(self.program)):
                self.program[card] = None
            self.cursor_index = 0
            self.change_callback()

    def cursor_index_plus(self):
        """
        Change selecting cursor position to the next one.
        """
        if not self.selection_confirmed:
            max_cursor_index = len(self.program) - 1
            if self.cursor_index < max_cursor_index:
                self.cursor_index += 1

    def cursor_index_minus(self):
        """
        Change selecting cursor position to the previous one.
        """
        if not self.selection_confirmed:
            if self.cursor_index > 0:
                self.cursor_index -= 1

    def switch_power_down(self):
        """
        Switch power down status between True and False.
        When it is True the Robot doesn't play this round.
        """
        if not self.selection_confirmed:
            if not self.power_down:
                self.power_down = True
            else:
                self.power_down = False
            self.change_callback()

    def confirm_selection(self):
        """
        When Power Down is switched on or all cards are chosen,
        it is possible to confirm selection.
        Additionally when Power Down is switched on,
        the cards from hand are returned.
        """
        if None not in self.program or self.power_down:
            if self.power_down:
                self.return_cards()
            self.selection_confirmed = True
            self.change_callback()
