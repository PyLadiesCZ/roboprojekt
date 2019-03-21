"""
Backend file contains functions for the game logic.
"""
from pathlib import Path
import random
from util import Direction, Rotation, HoleTile, get_next_coordinates
from loading import get_board

MAX_DAMAGE_VALUE = 10

class Robot:
    def __init__(self, direction, path, path_front, coordinates):
        self.direction = direction
        self.path = path
        self.path_front = path_front
        self.coordinates = coordinates
        self.start_coordinates = coordinates
        # program = cards on hand, list.
        # currently testing's value, to be removed
        self.program = [RotationCard(200, Rotation.LEFT), MovementCard(100, 2)]
        self.lives = 3
        self.flags = 0
        self.damages = 4
        self.power_down = False

    @property
    # More info about @property decorator - official documentation:
    # https://docs.python.org/3/library/functions.html#property
    def inactive(self):
        """
        Return True if robot is inactive (not on the game board).

        All inactive robots have coordinates None.
        """
        return self.coordinates == None

    def __repr__(self):
        return "<Robot {} {} {} Lives: {} Flags: {} Damages: {}, Inactive: {}>".format(
            self.direction, self.path, self.coordinates, self.lives, self.flags,
            self.damages, self.inactive)

    def walk(self, distance, state, direction=None):
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
            self.walk((-distance), state, direction.get_new_direction(Rotation.U_TURN))
        else:
            for step in range(distance):
                # Check the absence of a walls before moving.
                if not check_the_absence_of_a_wall(self.coordinates, direction, state):
                    break

                next_coordinates = get_next_coordinates(self.coordinates, direction)
                robot_in_the_way_index = check_robot_in_the_way(state, next_coordinates)

                # Move robot in the way.
                if robot_in_the_way_index is not None:
                        state.robots[robot_in_the_way_index].walk(1, state, direction)
                        # Check that robot moved.
                        if state.robots[robot_in_the_way_index].coordinates == next_coordinates:
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

        When robot is moved by game elements (convoyer belt or pusher),
        he doesn't have enough power to push other robots. If there is a robot
        in the way, the movement is stopped.
        """
        for step in range(distance):
            # Check walls before moving.
            if not check_the_absence_of_a_wall(self.coordinates, direction, state):
                break
            # There is no wall. Get next coordinates.
            next_coordinates = get_next_coordinates(self.coordinates, direction)
            # Check robots on the next tile before moving.
            robot_in_the_way_index = check_robot_in_the_way(state, next_coordinates)

            if robot_in_the_way_index is not None:
                # There is a robot on the next tile.
                # Robot can't be moved.
                break

            # There isn't a robot on the next tile. Robot will be moved.
            self.coordinates = next_coordinates
            # Check hole on next coordinates.
            self.fall_into_hole(state)
            # If robot falls into hole, he becomes inactive.
            if self.inactive:
                break

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

    def apply_card_effect(self, state):
        """
        Get the current card (depending on register) and perform the card effect.
        If the card's effect is move - it calls robot's method walk,
        if it is rotation - robot's method rotate.

        TODO: resolve card's priority
        """
        # card on an index of a current register
        current_card = self.program[state.register - 1]

        if isinstance(current_card, MovementCard):
            self.walk(current_card.distance, state)

        if isinstance(current_card, RotationCard):
            self.rotate(current_card.rotation)

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
                    robot_in_the_way_index = check_robot_in_the_way(state, next_coordinates)

                    # There is a robot, shoot him and break the cycle (only one gets shot).
                    if robot_in_the_way_index is not None:
                        state.robots[robot_in_the_way_index].be_damaged()
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
            return state.sizes[1] - self.coordinates[1]
        if self.direction == Direction.S:
            return self.coordinates[1] + 1
        if self.direction == Direction.E:
            return state.sizes[0] - self.coordinates[0]
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


class RotationCard(Card):
    def __init__(self, priority, value):
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


class State:
    def __init__(self, board, robots, sizes):
        self._board = board
        self.robots = robots
        self.sizes = sizes
        self.register = 1

    def __repr__(self):
        return "<State {} {}>".format(self._board, self.robots)

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


def get_starting_coordinates(board):
    """
    Get starting coordinates for robots.

    board: dictionary returned by get_board().

    Return a list with coordinates of starting tiles.

    Find the objects which are starting tiles (matching attribute path of Tile object),
    then add coordinate of those tiles to the list of starting coordinates.
    """
    starting_coordinates = []
    for coordinate, tiles in board.items():
        for tile in tiles:
            # range(9) because there may be max. 8 starting squares
            for i in range(9):
                if tile.path == ("./img/squares/png/starting_square0{}.png".format(i)):
                    starting_coordinates.append(coordinate)
    return starting_coordinates


def get_robot_paths():
    """
    Return a list of paths to robots images.

    Using pathlib.Path library add all the files in given directory to the list.
    Ex. [PosixPath('img/robots_map/png/MintBot.png'), PosixPath('img/robots_map/png/terka_robot_map.png')].
    """
    robot_paths = []
    for robot_path in Path('./img/robots_map/png/').iterdir():  # search image file
        name = robot_path.name
        robot_front_path = './img/robots/png/' + name
        robot_paths.append((robot_path, robot_front_path))
    return robot_paths


def create_robots(board):
    """
    Place robots on starting tiles.

    board: dictionary returned by get_board()

    Return list of robots on the starting tiles of the board.

    Initialize Robot objects on the starting tiles coordinates with random
    choice of robot's avatar on particular tile.
    Once the robot is randomly chosen, he is removed from the list
    (he cannot appear twice on the board).
    On the beginning all the Robot objects have implicit 0 degree direction.
    """
    starting_coordinates = get_starting_coordinates(board)
    robot_paths = get_robot_paths()
    robots_start = []
    for coordinate in starting_coordinates:
        # Condition to assure no exception in case robot_paths is shorter
        # than coordinate's list.
        if robot_paths:
            paths = random.choice(robot_paths)
            robot_paths.remove(paths)
            path, path_front = paths
            robot = Robot(Direction.N, path, path_front, coordinate)
            robots_start.append(robot)
    return robots_start


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


def get_start_state(map_name):
    """
    Get starting state of game.

    map_name: path to map file. Currently works only for .json files from Tiled 1.2

    Create board and robots on starting squares, initialize State object
    containing Tile and Robot object as well as the map size.

    Return State object.
    """
    board = get_board(map_name)
    tile_count = get_tile_count(board)
    robots_start = create_robots(board)
    state = State(board, robots_start, tile_count)
    return state


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
            # Return index of robot that is in the way.
            return state.robots.index(robot)

    # There are no robots, return None
    return None



def apply_tile_effects(state):
    """
    Apply the effects according to game rules.

    The function name is not entirely exact: the whole register phase actions take place
    (both tiles and robot's effects).
    """
    # Activate belts
        # 1) Express belts move 1 space
        # 2) Express belts and normal belts move 1 space

    # Activate pusher
    for robot in [robot for robot in state.robots if not robot.inactive]:
        for tile in state.get_tiles(robot.coordinates):
            tile.push_robot(robot, state)
            if robot.inactive:
                break

    # Activate gear
    for robot in [robot for robot in state.robots if not robot.inactive]:
        for tile in state.get_tiles(robot.coordinates):
            tile.rotate_robot(robot)

    # Activate laser
    for robot in [robot for robot in state.robots if not robot.inactive]:
        for tile in state.get_tiles(robot.coordinates):
            tile.shoot_robot(robot, state)
            if robot.inactive:
                break

    # Activate robot laser
    for robot in [robot for robot in state.robots if not robot.inactive]:
        robot.shoot(state)

    # Collect flags, repair robots
    for robot in [robot for robot in state.robots if not robot.inactive]:
        for tile in state.get_tiles(robot.coordinates):
            tile.collect_flag(robot)
            tile.repair_robot(robot, state)

    # after 5th register the inactive robots are back to the start
    if state.register == 5:
        set_robots_for_new_turn(state)


def set_robots_for_new_turn(state):
    """
    After 5th register there comes evaluation of the robots' state.
    "Dead" robots who don't have any lives left, are deleted from the robot's lists.

    "Inactive" robots who have lost one life during the round,
    will reboot on starting coordinates.
    """

    # Delete robots with zero lives
    state.robots = [robot for robot in state.robots if robot.lives > 0]
    for robot in state.robots:
        #Robot will now ressurect at his starting coordinates
        if robot.inactive:
            robot.coordinates = robot.start_coordinates
            robot.damages = 0
            robot.direction = Direction.N
