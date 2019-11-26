"""
Backend file contains functions for the game logic.
"""
from collections import OrderedDict
from random import shuffle
import yaml

from util_backend import Direction, Rotation, get_next_coordinates
from tile import HoleTile
from loading import get_board, get_map_data, board_from_data


MAX_CARD_COUNT = 9
MAX_DAMAGE_VALUE = 10


class NoCardError(LookupError):
    """Raised when a robot doesn't have a card for the given register."""


class CardNotKnownError(LookupError):
    """Raised when a card doesn't belong to any known type."""


# Load of robots displayed names in file robots.yaml
with open('robots.yaml', encoding='utf-8') as robot_file:
    robot_displayed_names = yaml.safe_load(robot_file)


class Robot:
    def __init__(self, direction, coordinates, name):
        self.direction = direction
        self.coordinates = coordinates
        self.start_coordinates = coordinates
        self.program = [None, None, None, None, None]
        self.lives = 3
        self.flags = 0
        self.damages = 0
        self.permanent_damages = 0
        self.power_down = False
        self.name = name
        self.displayed_name = robot_displayed_names[self.name]["displayed_name"]
        self.selection_confirmed = False
        self.card_indexes = []
        self.winner = False

    @property
    # More info about @property decorator - official documentation:
    # https://docs.python.org/3/library/functions.html#property
    def inactive(self):
        """
        Return True if robot is inactive (not on the game board).
        All inactive robots have coordinates None.
        """
        return self.coordinates is None

    @property
    def unblocked_cards(self):
        """
        Count robot´s unblocked cards.
        """
        damages = self.damages + self.permanent_damages
        if damages > 4:
            return MAX_CARD_COUNT - damages
        else:
            return 5

    def __repr__(self):
        return "<Robot {} {} {} Lives: {} Flags: {} Damages: {} \
                Permanent_damages: {} Inactive: {} Selection_confirmed: {} \
                Unblocked_cards: {} Winner: {}>".format(
                self.name, self.direction, self.coordinates, self.lives, self.flags,
                self.damages, self.permanent_damages, self.inactive, self.selection_confirmed,
                self.unblocked_cards, self.winner)

    def as_dict(self):
        """
        Return robot´s info as dictionary for sending with server.
        """
        return {"robot_data":
                {"name": self.name, "coordinates": self.coordinates,
                 "lives": self.lives, "flags": self.flags,
                 "damages": self.damages,
                 "permanent_damages": self.permanent_damages,
                 "power_down": self.power_down,
                 "direction": self.direction.value,
                 "start_coordinates": self.start_coordinates,
                 "selection_confirmed": self.selection_confirmed,
                 "unblocked_cards": self.unblocked_cards,
                 "winner": self.winner,
                 "displayed_name": self.displayed_name}}

    @classmethod
    def from_dict(cls, robot_description):
        """
        Return robot from JSON data received from server."
        """
        robot_description = robot_description["robot_data"]
        direction = Direction(robot_description["direction"])
        if robot_description["coordinates"] == None:
            coordinates = None
        else:
            coordinates = tuple(robot_description["coordinates"])
        name = robot_description["name"]
        robot = cls(direction, coordinates, name)
        robot.lives = robot_description["lives"]
        robot.flags = robot_description["flags"]
        robot.damages = robot_description["damages"]
        robot.permanent_damages = robot_description["permanent_damages"]
        robot.power_down = robot_description["power_down"]
        robot.start_coordinates = robot_description["start_coordinates"]
        robot.selection_confirmed = robot_description["selection_confirmed"]
        robot.winner = robot_description["winner"]
        robot.displayed_name = robot_description["displayed_name"]
        return robot

    def select_cards(self, state):
        """
        Set robot's program with chosen cards.
        Left dealt cards are moved to available cards, which are shuffled
        and if robot didn´t choose all cards to his program,
        they are replaced by random cards.
        """
        for program_index, dealt_card_index in enumerate(self.card_indexes):
            if self.program[program_index] is None and dealt_card_index is not None:
                card = self.dealt_cards[dealt_card_index]
                self.dealt_cards[dealt_card_index] = None
                self.program[program_index] = card
        self.card_indexes = []

        available_cards = []
        while self.dealt_cards:
            card = self.dealt_cards.pop()
            if card is not None:
                available_cards.append(card)
        shuffle(available_cards)

        for index, card in enumerate(self.program):
            if card is None:
                card = available_cards.pop()
                self.program[index] = card

        state.past_deck.extend(available_cards)
        available_cards.clear()

    def walk(self, distance, state, direction=None, push_others=True, log=True):
        """
        Move a robot to next coordinates based on his direction.
        Optional argument:
            direction - Default value is set to robot's direction.
        When robot walks, he can move other robots in the way.
        """
        if direction is None:
            direction = self.direction

        # Robot can go backwards - then his distance is -1.
        # In this case he walks 1 step in the direction opposite to the given one.
        # He can still move the other robots on the way.
        if distance < 0:
            self.walk((-distance), state, direction.get_new_direction(Rotation.U_TURN),
                      push_others=push_others)
        else:
            for step in range(distance):
                # Check the absence of a walls before moving.
                if not state.check_the_absence_of_a_wall(self.coordinates, direction):
                    break

                # There is no wall. Get next coordinates.
                next_coordinates = get_next_coordinates(self.coordinates, direction)
                # Check robots on the next tile before moving.
                robot_in_the_way = state.check_robot_in_the_way(next_coordinates)

                # Move robot in the way.
                if robot_in_the_way:
                    if push_others:
                        # Move other robot, but don't log it as a separate action
                        robot_in_the_way.walk(1, state, direction, log=False)
                        # Check that robot moved.
                        if robot_in_the_way.coordinates == next_coordinates:
                            break
                    else:
                        break

                # Robot walks to next coordinates.
                self.coordinates = next_coordinates
                if log:
                    state.record_log()
                # Check hole on next coordinates.
                self.fall_into_hole(state)
                # If robot falls into hole, he becomes inactive.
                if self.inactive:
                    break

    def move(self, direction, distance, state):
        """
        Move a robot to next coordinates according to direction of the move.

        When robot is moved by game elements (conveyor belt or pusher),
        he doesn't have enough power to push other robots. If there is a robot
        in the way, the movement is stopped.
        """
        self.walk(distance=distance, state=state, direction=direction, push_others=False)

    def die(self, state):
        """
        Robot lose life and skip rest of game round.
        Robot is moved out of game board for the rest of the round.
        """
        state.record_log()
        if self.lives > 0:
            self.lives -= 1

        if self.lives <= 0:
            self.permanent_damages += 1

        self.coordinates = None
        state.record_log()

    def rotate(self, where_to, state):
        """
        Rotate robot according to a given direction.
        """
        self.direction = self.direction.get_new_direction(where_to)
        state.record_log()

    def fall_into_hole(self, state):
        """
        Check tiles on robot's coordinates for HoleTile and apply its effect.
        """

        if self.coordinates != None:
            for tile in state.get_tiles(self.coordinates):
                tile.kill_robot(state, self)
                if self.inactive:
                    break

    def shoot(self, state):
        """
        Shoot in robot's direction.
        If there is a wall on the way, the robot's laser stops (it can't pass it).
        If there is a robot on the way, he gets shot and the laser ends there.
        If a robot has activated Power Down for this register, he can't shoot.
        The check is performed from robot's position till the end of the board in robot's direction.
        """

        if not self.power_down:
            distance_till_end = self.get_distance_to_board_end(state)

            # First coordinates are robot's coordinates - wall must be checked
            next_coordinates = self.coordinates

            for step in range(distance_till_end):
                # Check if there is a robot on the next coordinates.
                # Skip this if the shooting robot's current coordinates are checked
                if next_coordinates != self.coordinates:
                    robot_in_the_way = state.check_robot_in_the_way(next_coordinates)

                    # There is a robot, shoot him and break the cycle (only one gets shot).
                    if robot_in_the_way:
                        robot_in_the_way.be_damaged(state)
                        break

                # Check if there is a wall, if is: end of shot.
                if not state.check_the_absence_of_a_wall(next_coordinates, self.direction):
                    break

                # No robots or walls on the coordinates, check one step further.
                else:
                    next_coordinates = get_next_coordinates(next_coordinates, self.direction)

    def be_damaged(self, state, strength=1):
        """
        Give one or more damages to the robot.
        If the robot has reached the maximum damage value, he gets killed.
        Strengh: optional argument, meaning how many damages should be added.
        By default it is 1 - the value of robot's laser.
        When the damage is performed by laser tile, there can be bigger number.
        """
        if self.permanent_damages > 0:
            max_robot_damages = MAX_DAMAGE_VALUE - self.permanent_damages
        else:
            max_robot_damages = MAX_DAMAGE_VALUE

        if self.damages < (max_robot_damages - strength):
            # Laser won't kill robot, but it will damage robot.
            self.damages += strength
        else:
            # Robot is damaged so much that laser kills it.
            self.die(state)
        state.record_log()

    def clear_robot_attributes(self, state):
        """
        Clear robot attributes at the end of round.
        If robot has blocked cards, it is left in his program.
        """
        for index in range(self.unblocked_cards):
            card = self.program[index]
            state.past_deck.append(card)
            self.program[index] = None
        self.selection_confirmed = False
        self.power_down = False

    def freeze(self):
        """
        Switch on power down and confirm selection for robot.
        """
        self.power_down = True
        self.selection_confirmed = True

    def change_start_coordinates(self, state):
        """
        Check if the other robots have the same starting coordinates as
        own current coordinates. If so, don't change the starting coordinates.
        If there is no other robot with the same starting coordinates,
        change the start coordinates to current ones.
        """
        for robot in state.robots:
            if robot.start_coordinates == self.coordinates:
                return
        else:
            if self.start_coordinates != self.coordinates:
                self.start_coordinates = self.coordinates
                state.record_log()

    def select_blocked_cards_from_program(self):
        """
        Return a list of blocked cards from robot program.
        """
        blocked_cards = []
        for card in self.program:
            if card is not None:
                blocked_cards.append(card)
        return blocked_cards

    def get_distance_to_board_end(self, state):
        """
        Get the distance from the robot's coordinates to the end of the board in robot's direction.
        Measured number is in the count of tiles between the robot and the board's edge.
        """

        if self.direction == Direction.N:
            return state.tile_count[1] - self.coordinates[1]
        if self.direction == Direction.S:
            return self.coordinates[1] + 1
        if self.direction == Direction.E:
            return state.tile_count[0] - self.coordinates[0]
        if self.direction == Direction.W:
            return self.coordinates[0] + 1


class Card:
    def __init__(self, priority):
        self.priority = priority  # int - to decide who goes first

    def __gt__(self, other):
        if other.priority < self.priority:
            return True
        else:
            return False

    @classmethod
    def from_dict(cls, card_description):
        """
        Return a card instance according to the given type.
        In case type is not known raise CardNotKnownError.
        """
        if "MovementCard" in card_description:
            return MovementCard.from_dict(card_description)
        elif "RotationCard" in card_description:
            return RotationCard.from_dict(card_description)
        else:
            raise CardNotKnownError


class MovementCard(Card):
    def __init__(self, priority, value):
        self.distance = value
        super().__init__(priority)

    @property
    def name(self):
        if self.distance == -1:
            return "back_up"
        else:
            return "move{}".format(self.distance)

    def __repr__(self):
        return "<{} {} {}>".format(self.name, self.priority, self.distance)

    def apply_effect(self, robot, state):
        """
        Card calls robot's method walk.
        """
        robot.walk(self.distance, state)

    def as_dict(self):
        """
        Return card´s info as dictionary for sending with server.
        """
        return {"MovementCard":
                {"priority": self.priority,
                 "distance": self.distance,
                 }}

    @classmethod
    def from_dict(cls, card_description):
        """
        Return MovementCard from data received from server.
        """
        priority = card_description["MovementCard"]["priority"]
        distance = card_description["MovementCard"]["distance"]
        return MovementCard(priority, distance)


class RotationCard(Card):
    def __init__(self, priority, value):
        if isinstance(value, int):
            value = Rotation(value)
        self.rotation = value
        super().__init__(priority)

    @property
    def name(self):
        if self.rotation == Rotation.RIGHT:
            return "right"
        if self.rotation == Rotation.LEFT:
            return "left"
        else:
            return "u_turn"

    def __repr__(self):
        return "<{} {} {}>".format(self.name, self.priority, self.rotation)

    def apply_effect(self, robot, state):
        """
        Card calls robot's method rotate.
        """
        robot.rotate(self.rotation, state)

    def as_dict(self):
        """
        Return card´s info as dictionary for sending with server.
        """
        return {"RotationCard":
                {"priority": self.priority,
                 "rotation": self.rotation.value,
                 }}

    @classmethod
    def from_dict(cls, card_description):
        """
        Return RotationCard from data received from server.
        """
        priority = card_description["RotationCard"]["priority"]
        rotation = card_description["RotationCard"]["rotation"]
        return RotationCard(priority, Rotation(rotation))


class State:
    def __init__(self, board, robots):
        self._board = board
        self.robots = robots
        self.tile_count = self.get_tile_count()
        self.present_deck = self.create_card_pack()
        self.past_deck = []
        self.game_round = 1
        self.winners = []
        self.flag_count = self.get_flag_count()
        self.log = []

    def __repr__(self):
        return "<State {} {}>".format(self._board, self.robots)

    @classmethod
    def whole_from_dict(cls, data):
        """
        Create game state from JSON data received from server.
        """
        map_data = data["game_state"]["board"]
        board = board_from_data(map_data)
        robots = cls.robots_from_dict(cls, data["game_state"])
        return cls(board, robots)

    def robots_from_dict(self, data):
        """
        Return list of robots with data sent from server.
        """
        robots = []
        for robot_description in data["robots"]:
            robot = Robot.from_dict(robot_description)
            robots.append(robot)
        return robots

    def whole_as_dict(self, map_name):
        """
        Return whole state as dictionary for sending with server.
        """
        return {"game_state": {
                "board": get_map_data(map_name),
                **self.robots_as_dict(), }}

    def robots_as_dict(self):
        """
        Return robots from state as dictionary for sending with server.
        """
        return {"robots": [robot.as_dict() for robot in self.robots]}

    def record_log(self):
        new_entry = self.robots_as_dict()
        if self.log and self.log[-1] == new_entry:
            # The new entry is the same as the previous one.
            return
        self.log.append(new_entry)

    @classmethod
    def get_start_state(cls, map_name):
        """
        Get start state of game.

        map_name: path to map file. Create board and robots on start tiles,
        initialize State object with them.
        """
        board = get_board(map_name)
        robots_start = create_robots(board)
        state = cls(board, robots_start)
        for robot in state.robots:
            state.deal_cards(robot)
        return state

    def get_tile_count(self):
        """
        From the board coordinates get the count of tiles
        in horizontal (x) and vertical (y) ax.
        """
        x_set = set()
        y_set = set()
        for coordinate in self._board.keys():
            x, y = coordinate
            x_set.add(x)
            y_set.add(y)
        return len(x_set), len(y_set)

    def get_tiles(self, coordinates):
        """
        Get tiles on requested coordinates.

        coordinates: tuple of x and y coordinate
        Return a list of tiles or return hole tile if coordinates are out of the board.
        """
        if coordinates in self._board:
            return self._board[coordinates]
        else:
            # Coordinates are out of game board.
            # Return hole tile.
            return [HoleTile()]

    def get_active_robots(self):
        """
        Yield all active robots.
        """
        for robot in self.robots:
            if not robot.inactive:
                yield robot

    def check_robot_in_the_way(self, coordinates):
        """
        Check if there are robot on the next coordinates.

        Return index of the robot on the way from given point.
        It there are no robots, return None.
        """
        # Check robots on the next tile.
        for robot in self.robots:
            if robot.coordinates == coordinates:
                # Return robot that is in the way.
                return robot
        # There are no robots, return None
        return None

    def check_the_absence_of_a_wall(self, coordinates, direction):
        """
        Check the absence of a wall in the direction of the move.

        coordinates: tuple of x and y coordinate
        direction: object of Direction class
        Return a boolean.
        True - There isn't wall, robot can move.
        False - There is wall, robot can't move.
        """
        old_tiles = self.get_tiles(coordinates)
        # Current tile: Check wall in the direction of next move.
        for tile in old_tiles:
            move_from = tile.can_move_from(direction)
            if not move_from:
                # Current tile: There is a wall in the direction of the move.
                return False

        # There is no wall, so get next coordinates.
        next_coordinates = get_next_coordinates(coordinates, direction)
        # Get new list of tiles.
        new_tiles = self.get_tiles(next_coordinates)
        # Check wall on the next tile in the direction of the move.
        for tile in new_tiles:
            move_to = tile.can_move_to(direction)
            if not move_to:
                # Next tile: There is a wall in the direction of the move.
                return False
        return True

    def move_belts(self):
        """
        Move robots on conveyor belts.
        """
        # According to rules:
        # First, express belts move robots by one tile (express attribute is set to True).
        # Then all belts move robots by one tile (express attribute is set to False).
        for express_belts in True, False:
            # Get robots next coordinates after move of conveyor belts
            robots_next_coordinates = self.get_next_coordinates_for_belts(express_belts)
            # Solve blocked robots (colliding and swapping robots)
            for blocked_func in get_colliding_robots, get_swapping_robots:
                while True:
                    blocked_robots = blocked_func(robots_next_coordinates)
                    if not blocked_robots:
                        break
                    else:
                        # For blocked robots set next coordinates to their current.
                        for robot in blocked_robots:
                            robots_next_coordinates[robot] = robot.coordinates

            # All collision sorted, move robots to new coordinates
            for robot in robots_next_coordinates:
                if robot.coordinates != robots_next_coordinates[robot]:
                    # Get direction of belt movement
                    direction = get_direction_from_coordinates(
                        robot.coordinates,
                        robots_next_coordinates[robot]
                    )
                    # Check if the next tile is rotating belt.
                    for tile in self.get_tiles(robots_next_coordinates[robot]):
                        tile.rotate_robot_on_belt(robot, direction, self)
                robot.coordinates = robots_next_coordinates[robot]
            self.record_log()
            for robot in self.robots:
                robot.fall_into_hole(self)

    def get_next_coordinates_for_belts(self, express_belts):
        """
        Get all robot's next coordinates after move of certain type of conveyor belts.

        express_belts: a boolean, True - for express belts, False - for all belts.
        Return a dictionary of robots as keys and their next coordinates as values.
        """
        robots_next_coordinates = {}
        for robot in self.get_active_robots():
            for tile in self.get_tiles(robot.coordinates):
                if tile.check_belts(express_belts):
                    belt_direction = tile.direction.get_new_direction(tile.direction_out)
                    if self.check_the_absence_of_a_wall(robot.coordinates, belt_direction):
                        # Get next coordinates of robots on belts
                        robots_next_coordinates[robot] = get_next_coordinates(
                            robot.coordinates, belt_direction)
                        break
                # Other robots will have the same coordinates
                robots_next_coordinates[robot] = robot.coordinates
        return robots_next_coordinates

    def apply_tile_effects(self, register):
        """
        Apply the effects according to game rules.

        The method name is not entirely exact: the whole register phase actions
        take place (both tiles and robot's effects).
        """

        # Activate belts
        self.move_belts()

        # Activate pusher
        active_pusher = False
        for robot in self.get_active_robots():
            for tile in self.get_tiles(robot.coordinates):
                if tile.push_robot(robot, self, register):
                    active_pusher = True
                if robot.inactive:
                    break
        if active_pusher:
            self.record_log()

        # Activate gear
        active_gear = False
        for robot in self.get_active_robots():
            for tile in self.get_tiles(robot.coordinates):
                if tile.rotate_robot(robot, self):
                    active_gear = True
        if active_gear:
            self.record_log()

        # Activate laser
        active_laser = False
        for robot in self.get_active_robots():
            for tile in self.get_tiles(robot.coordinates):
                if tile.shoot_robot(robot, self):
                    active_laser = True
                if robot.inactive:
                    break
        if active_laser:
            self.record_log()

        # Activate robot laser
        for robot in self.get_active_robots():
            robot.shoot(self)

        # Collect flags, repair robots
        for robot in self.get_active_robots():
            for tile in self.get_tiles(robot.coordinates):
                tile.collect_flag(robot, self)
                tile.set_new_start(robot, self)

    def set_robots_for_new_turn(self):
        """
        After 5th register there comes evaluation of the robots' state.
        "Inactive" robots who have lost one life during the round,
        will reboot on start coordinates.
        """
        self.robots = [robot for robot in self.robots if robot.permanent_damages < 10]
        for robot in self.robots:
            for tile in self.get_tiles(robot.coordinates):
                tile.repair_robot(robot, self)
            # Robot will now ressurect at his start coordinates
            if robot.inactive:
                robot.coordinates = robot.start_coordinates
                robot.damages = 0
                self.record_log()

    def get_robots_ordered_by_cards_priority(self, register):
        """
        Get all the active robots, sort them according to the priority of their
        current card.
        If any of the robots misses the card, raise NoCardError.
        """
        try:
            robot_cards = [(robot, robot.program[register])
                           for robot in self.get_active_robots() if not robot.power_down]
            robot_cards.sort(key=lambda item: item[1], reverse=True)
            return robot_cards

        except TypeError:
            raise NoCardError

    def apply_register(self, register):
        """
        For the given register sort the robot's list according to card's priorities.
        Apply cards effects on the sorted robots.
        """
        robot_cards = self.get_robots_ordered_by_cards_priority(register)
        for robot, card in robot_cards:
            if not robot.inactive:
                card.apply_effect(robot, self)

    def apply_all_effects(self, registers=5):
        """
        Apply all game effects: for the given number of iterations
        perform robot's cards effects and tile effects on a given game state.
        At the end ressurect the inactive robots to their starting coordinates.
        registers: default iterations count is 5, can be changed for testing purposes.
        """
        for register in range(registers):
            # try -  except was introduced for devel purposes - it may happen that
            # robots have no card on hand and we still want to try loading the game
            try:
                # Check the card's priority
                self.apply_register(register)

            except NoCardError:
                print("No card on hand, continue to tile effects.")
                pass

            self.apply_tile_effects(register)

        # After last register ressurect the robots to their starting coordinates.
        self.set_robots_for_new_turn()

    def play_round(self):
        """
        Apply effects of cards and tiles.
        Erase robot's damages if they chose power down for this round.
        Check if somebody has won.
        Robots' attributes are cleared and new cards dealt.
        """
        for robot in self.robots:
            robot.select_cards(self)
            if robot.power_down:
                robot.damages = 0
        self.apply_all_effects()
        self.check_winner()
        self.game_round += 1
        for robot in self.robots:
            robot.clear_robot_attributes(self)
            self.deal_cards(robot)

    def create_card_pack(self):
        """
        Create and shuffle pack of cards: 42 movement and 42 rotation cards
        with different values and priorities.
        """
        movement_cards = [(-1, 6, 250),
                          (1, 18, 300),
                          (2, 12, 400),
                          (3, 6, 500),
                          ]
        rotation_cards = [(Rotation.U_TURN, 6, 50),
                          (Rotation.LEFT, 18, 100),
                          (Rotation.RIGHT, 18, 200),
                          ]
        present_deck = []

        for movement, cards_count, first_number in movement_cards:
            for i in range(cards_count):
                # [MovementCard(690, -1)...][]
                present_deck.append(MovementCard(first_number + i*5, movement))

        for rotation, cards_count, first_number in rotation_cards:
            for i in range(cards_count):
                # [RotationCard(865, Rotation.LEFT)....]
                present_deck.append(RotationCard(first_number + i*5, rotation))
        shuffle(present_deck)
        return present_deck

    def deal_cards(self, robot):
        """
        Deal the cards for robot - he gets one card less for every damage he's got.
        Take the first cards from the card pack.
        """
        # Maximum number of cards is 9.
        # Robot's damages reduce the count of dealt cards - each damage one card.
        robot.dealt_cards = []
        for number in range(MAX_CARD_COUNT-robot.damages-robot.permanent_damages):
            if not self.present_deck:
                self.present_deck.extend(self.past_deck)
                self.past_deck.clear()
                shuffle(self.present_deck)
            robot.dealt_cards.append(self.present_deck.pop())

    def cards_and_game_round_as_dict(self, cards, blocked_cards):
        """
        Take a list of cards instances and return them as dictionary.
        """
        card_pack = []
        for card in cards:
            card_pack.append(card.as_dict())
        blocked_cards_pack = []
        for card in blocked_cards:
            blocked_cards_pack.append(card.as_dict())

        return {"cards": card_pack, "blocked_cards": blocked_cards_pack,
                "current_game_round": self.game_round}

    def cards_from_dict(self, cards):
        """
        Create a list of card instances from dictionary given as an argument.
        """
        card_pack = []
        for card in cards:
            card_pack.append(Card.from_dict(card))
        return card_pack

    def count_confirmed_selections(self):
        """
        Return number of confirmed selections.
        """
        confirmed_count = 0
        for robot in self.robots:
            if robot.selection_confirmed:
                confirmed_count += 1
        return confirmed_count

    def get_flag_count(self):
        """
        Return number of flags on the map.
        """
        flag_count = 0
        weight, height = self.tile_count
        for x in range(0, weight):
            for y in range(0, height):
                tiles = self.get_tiles((x, y))
                for tile in tiles:
                    if tile.type == "flag":
                        flag_count += 1
        return flag_count

    def check_winner(self):
        """
        Check if somebody has won (robot collected all flags).
        Return list of winner(s).
        """
        if not self.winners:
            for robot in self.robots:
                if robot.flags == self.flag_count:
                    self.winners.append(robot.displayed_name)
                    robot.winner = True
        return self.winners


def get_robot_names():
    """
    Return a list of robots names (names of the files with robots avatars).
    """
    robot_names = list(robot_displayed_names.keys())
    return robot_names


def get_start_tiles(board, tile_type="start"):
    """
    Get initial tiles for robots. It can be either start or stop tiles.

    board: dictionary returned by get_board().
    tile_type: choose the "stop" initial tile type if you want to get
    the final tiles (only for tests).
    By default it is "start", which results in reading classic start tiles.
    Create an ordered dictionary of all initial tiles in the board with initial
    tile number as a key and values: coordinates and tile_direction.
    OrderedDict is a structure that ensures the dictionary is stored
    in the order of the new keys being added.
    """

    robot_tiles = {}

    for coordinate, tiles in board.items():
        for tile in tiles:
            if tile.type == tile_type:
                robot_tiles[tile.number] = {"coordinates": coordinate,
                                            "tile_direction": tile.direction}

    # Sort created dictionary by the first element - start tile number
    robot_tiles = OrderedDict(sorted(robot_tiles.items(), key=lambda stn: stn[0]))

    return robot_tiles


def create_robots(board):
    """
    Place robots on start tiles.

    board: dictionary returned by get_board()
    Initialize Robot objects on the start tiles coordinates with random
    choice of robot's avatar on particular tile.
    Once the robot is randomly chosen, he is removed from the list
    (he cannot appear twice on the board).
    Robots are placed on board in the direction of their start tiles.
    The robots are ordered according to their start tiles.
    """
    start_tiles = get_start_tiles(board)
    robots_on_start = []
    robot_names = get_robot_names()

    for start_tile_number, name in zip(start_tiles, robot_names):
        # Get direction and coordinates for the robot on the tile
        initial_direction = start_tiles[start_tile_number]["tile_direction"]
        initial_coordinates = start_tiles[start_tile_number]["coordinates"]

        # Create a robot, add him to robot's list
        robot = Robot(initial_direction, initial_coordinates, name)
        robots_on_start.append(robot)
    return robots_on_start


def get_colliding_robots(robots):
    """
    Get a list of robots, who would collide during belt movement.
    """
    colliding_robots = []
    for robot in robots.keys():
        # Check if there are duplicate values of next coordinates.
        if is_duplicate(robots, robot):
            colliding_robots.append(robot)
    return colliding_robots


def is_duplicate(data, key):
    """
    For input key check if its value is duplicate of other values in dictionary.
    """
    value = data[key]
    for current_key, current_value in data.items():
        if current_value == value and current_key != key:
            return True
    return False


def get_swapping_robots(robots):
    """
    Get list of robots, who would switch coordinates during belt movement.
    """
    swapping_robots = []
    for robot1, next_coordinates1 in robots.items():
        for robot2, next_coordinates2 in robots.items():
            if robot1 != robot2:
                if robot1.coordinates == next_coordinates2 and robot2.coordinates == next_coordinates1:
                    swapping_robots.append(robot1)
    return swapping_robots


def get_direction_from_coordinates(start_coordinates, stop_coordinates):
    """
    Get Direction class object according to change in coordinates.
    Work only for change by one tile.
    """
    x_stop, y_stop = stop_coordinates
    x_start, y_start = start_coordinates

    delta = (x_stop - x_start, y_stop - y_start)
    for direction in list(Direction):
        if direction.coor_delta == delta:
            return direction
