"""
Backend file contains functions for the game logic.
"""
from pathlib import Path
from collections import OrderedDict

from util import Direction, Rotation, get_next_coordinates
from tile import HoleTile
from loading import get_board, get_map_data

MAX_DAMAGE_VALUE = 10


class Robot:
    def __init__(self, direction, coordinates, name):
        self.direction = direction
        self.coordinates = coordinates
        self.start_coordinates = coordinates
        self.program = []
        self.lives = 3
        self.flags = 0
        self.damages = 4
        self.power_down = False
        self.name = name

        self._tile_number_for_tests = 0

    @property
    # More info about @property decorator - official documentation:
    # https://docs.python.org/3/library/functions.html#property
    def inactive(self):
        """
        Return True if robot is inactive (not on the game board).
        All inactive robots have coordinates None.
        """
        return self.coordinates is None

    def __repr__(self):
        return "<Robot {} {} {} Lives: {} Flags: {} Damages: {}, Inactive: {}>".format(
            self.name, self.direction, self.coordinates, self.lives, self.flags,
            self.damages, self.inactive)

    def as_dict(self):
        """
        Return robot´s info as dictionary for sending with server.
        """
        return {"name": self.name, "coordinates": self.coordinates, "lives": self.lives,
                "flags": self.flags, "damages": self.damages, "inactive": self.inactive}

    def walk(self, distance, state, direction=None, push_others=True):
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
                if not check_the_absence_of_a_wall(self.coordinates, direction, state):
                    break

                # There is no wall. Get next coordinates.
                next_coordinates = get_next_coordinates(self.coordinates, direction)
                # Check robots on the next tile before moving.
                robot_in_the_way = check_robot_in_the_way(state, next_coordinates)

                # Move robot in the way.
                if robot_in_the_way:
                    if push_others:
                        robot_in_the_way.walk(1, state, direction)
                        # Check that robot moved.
                        if robot_in_the_way.coordinates == next_coordinates:
                            break
                    else:
                        break

                # Robot walks to next coordinates.
                self.coordinates = next_coordinates
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

    def die(self):
        """
        Robot lose life and skip rest of game round.
        Robot is moved out of game board for the rest of the round.
        """
        self.lives -= 1
        self.coordinates = None

    def rotate(self, where_to):
        """
        Rotate robot according to a given direction.
        """
        self.direction = self.direction.get_new_direction(where_to)

    def fall_into_hole(self, state):
        """
        Check tiles on robot's coordinates for HoleTile and apply its effect.
        """

        for tile in state.get_tiles(self.coordinates):
            tile.kill_robot(self)
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
                    robot_in_the_way = check_robot_in_the_way(state, next_coordinates)

                    # There is a robot, shoot him and break the cycle (only one gets shot).
                    if robot_in_the_way:
                        robot_in_the_way.be_damaged()
                        break

                # Check if there is a wall, if is: end of shot.
                if not check_the_absence_of_a_wall(next_coordinates, self.direction, state):
                    break

                # No robots or walls on the coordinates, check one step further.
                else:
                    next_coordinates = get_next_coordinates(next_coordinates, self.direction)

    def be_damaged(self, strength=1):
        """
        Give one or more damages to the robot.
        If the robot has reached the maximum damage value, he gets killed.
        Strengh: optional argument, meaning how many damages should be added.
        By default it is 1 - the value of robot's laser.
        When the damage is performed by laser tile, there can be bigger number.
        """
        if self.damages < (MAX_DAMAGE_VALUE - strength):
            # Laser won't kill robot, but it will damage robot.
            self.damages += strength
        else:
            # Robot is damaged so much that laser kills it.
            self.die()

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
        robot.rotate(self.rotation)


class State:
    def __init__(self, board, robots):
        self._board = board
        self.robots = robots
        self.tile_count = get_tile_count(board)

    def __repr__(self):
        return "<State {} {}>".format(self._board, self.robots)

    def as_dict(self, map_name):
        """
        Return state as dictionary for sending with server
        """
        return {"board": get_map_data(map_name), "robots": [robot.as_dict() for robot in self.robots]}

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


def get_robot_names():
    """
    Return a list of robots names (names of the files with robots avatars).
    """
    robot_names = []
    for img in Path('./img/robots/png').iterdir():
        robot_name = img.stem
        robot_names.append(robot_name)
    return robot_names


def get_start_tiles(board, robot_tile_type=None):
    """
    Get initial tiles for robots. It can be either start or stop tiles.

    board: dictionary returned by get_board().
    robot_tile_type: choose the "stop" initial tile type if you want to get
    the final tiles (only for tests).
    By default it is None, which results in reading classic start tiles.
    Create an ordered dictionary of all initial tiles in the board with initial
    tile number as a key and values: coordinates and tile_direction.
    OrderedDict is a structure that ensures the dictionary is stored
    in the order of the new keys being added.
    """

    robot_tiles = {}

    for coordinate, tiles in board.items():
        for tile in tiles:
            if robot_tile_type == "stop":
                if tile.stop_properties_dict(coordinate) is not None:
                    robot_tiles[tile.number] = tile.stop_properties_dict(coordinate)
            else:
                if tile.properties_dict(coordinate) is not None:
                    robot_tiles[tile.number] = tile.properties_dict(coordinate)

    # Sort created dictionary by the first element - start tile number
    OrderedDict(sorted(robot_tiles.items(), key=lambda stn: stn[0]))

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


def get_start_state(map_name):
    """
    Get start state of game.

    map_name: path to map file. Currently works only for .json files from Tiled 1.2
    Create board and robots on start tiles, initialize State object
    containing Tile and Robot object as well as the map size.
    Return State object.
    """
    board = get_board(map_name)
    robots_start = create_robots(board)
    state = State(board, robots_start)
    return state


def get_tile_count(board):
    """
    From the board coordinates get the count of tiles in horizontal (x) and vertical (y) ax.
    Takes board: result of get_board() from loading module.
    """
    x_set = set()
    y_set = set()
    for coordinate in board.keys():
        x, y = coordinate
        x_set.add(x)
        y_set.add(y)
    return len(x_set), len(y_set)


def check_the_absence_of_a_wall(coordinates, direction, state):
    """
    Check the absence of a wall in the direction of the move.

    coordinates: tuple of x and y coordinate
    direction: object of Direction class
    state: object of State class
    Return a boolean.
    True - There isn't wall, robot can move.
    False - There is wall, robot can't move.
    """
    old_tiles = state.get_tiles(coordinates)
    # Current tile: Check wall in the direction of next move.
    for tile in old_tiles:
        move_from = tile.can_move_from(direction)
        if not move_from:
            # Current tile: There is a wall in the direction of the move.
            return False

    # There is no wall, so get next coordinates.
    next_coordinates = get_next_coordinates(coordinates, direction)
    # Get new list of tiles.
    new_tiles = state.get_tiles(next_coordinates)
    # Check wall on the next tile in the direction of the move.
    for tile in new_tiles:
        move_to = tile.can_move_to(direction)
        if not move_to:
            # Next tile: There is a wall in the direction of the move.
            return False

    return True


def check_robot_in_the_way(state, coordinates):
    """
    Check if there are robot on the next coordinates.
    Return index of the robot on the way from given point.
    It there are no robots, return None.
    """
    # Check robots on the next tile.
    for robot in state.robots:
        if robot.coordinates == coordinates:
            # Return robot that is in the way.
            return robot

    # There are no robots, return None
    return None


def move_belts(state):
    """
    Move robots on conveyor belts.
    """
    # According to rules:
    # First, express belts move robots by one tile (express attribute is set to True).
    # Then all belts move robots by one tile (express attribute is set to False).
    for express_belts in [True, False]:
        # Get robots next coordinates after move of conveyor belts
        robots_next_coordinates = get_next_coordinates_for_belts(state, express_belts)

        # Solve colliding robots
        while True:
            colliding_robots = get_colliding_robots(robots_next_coordinates)
            if not colliding_robots:
                break
            else:
                # For colliding robots set next coordinates to their current.
                for robot in colliding_robots:
                    robots_next_coordinates[robot] = robot.coordinates
        # Solve robots who would switch coordinates
        while True:
            swapping_robots = get_swapping_robots(robots_next_coordinates)
            if not swapping_robots:
                break
            else:
                # For swapping robots set next coordinates to their current.
                for robot in swapping_robots:
                    robots_next_coordinates[robot] = robot.coordinates

        # All collision sorted, move robots to new coordinates
        for robot in robots_next_coordinates:
            if robot.coordinates != robots_next_coordinates[robot]:
                # Get direction of belt movement
                direction = get_direction_from_coordinates(robot.coordinates, robots_next_coordinates[robot])
                # Check if the next tile is rotating belt.
                for tile in state.get_tiles(robots_next_coordinates[robot]):
                    tile.rotate_robot_on_belt(robot, direction)
            robot.coordinates = robots_next_coordinates[robot]


def get_next_coordinates_for_belts(state, express_belts):
    """
    Get all robot's next coordinates after move of certain type of conveyor belts.

    express_belts: a boolean, True - for express belts, False - for all belts.

    Return a dictionary of robots as keys and their next coordinates as values.
    """
    robots_next_coordinates = {}
    for robot in state.robots:
        for tile in state.get_tiles(robot.coordinates):
            if tile.check_belts(express_belts):
                # Get next coordinates of robots on belts
                robots_next_coordinates[robot] = get_next_coordinates(robot.coordinates, tile.direction.get_new_direction(tile.direction_out))
                break
            else:
                # Other robots will have the same coordinates
                robots_next_coordinates[robot] = robot.coordinates
    return robots_next_coordinates


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
    x, y = start_coordinates
    if (x, y + 1) == stop_coordinates:
        return Direction.N
    elif (x, y - 1) == stop_coordinates:
        return Direction.S
    elif (x + 1, y) == stop_coordinates:
        return Direction.E
    elif (x - 1, y) == stop_coordinates:
        return Direction.W


def apply_tile_effects(state, round):
    """
    Apply the effects according to game rules.
    The function name is not entirely exact: the whole register phase actions take place
    (both tiles and robot's effects).
    """
    # Activate belts
    move_belts(state)

    # Activate pusher
    for robot in state.get_active_robots():
        for tile in state.get_tiles(robot.coordinates):
            tile.push_robot(robot, state, round)
            if robot.inactive:
                break

    # Activate gear
    for robot in state.get_active_robots():
        for tile in state.get_tiles(robot.coordinates):
            tile.rotate_robot(robot)

    # Activate laser
    for robot in state.get_active_robots():
        for tile in state.get_tiles(robot.coordinates):
            tile.shoot_robot(robot, state)
            if robot.inactive:
                break

    # Activate robot laser
    for robot in state.get_active_robots():
        robot.shoot(state)

    # Collect flags, repair robots
    for robot in state.get_active_robots():
        for tile in state.get_tiles(robot.coordinates):
            tile.collect_flag(robot)
            tile.repair_robot(robot, state, round)


def set_robots_for_new_turn(state):
    """
    After 5th register there comes evaluation of the robots' state.
    "Dead" robots who don't have any lives left, are deleted from the robot's lists.
    "Inactive" robots who have lost one life during the round,
    will reboot on start coordinates.
    """

    # Delete robots with zero lives
    state.robots = [robot for robot in state.robots if robot.lives > 0]
    for robot in state.robots:
        # Robot will now ressurect at his start coordinates
        if robot.inactive:
            robot.coordinates = robot.start_coordinates
            robot.damages = 0
            robot.direction = Direction.N


def play_the_game(state, rounds=5):
    """
    Play the whole game: for the given number of iterations
    perform robot's cards effects and tile effects on a given game state.
    At the end ressurect the inactive robots to their starting coordinates.
    rounds: default iterations count is 5, can be changed for testing purposes.
    """
    for round in range(rounds):
        for robot in state.get_active_robots():
            try:
                current_card = robot.program[round]
                current_card.apply_effect(robot, state)

            # If the program on hand is shorter than 5,
            # pass the error and go to tile effects
            except IndexError:
                pass
        apply_tile_effects(state, round)
    # After last round ressurect the robots to their starting coordinates.
    set_robots_for_new_turn(state)
