"""
Backend file contains functions for the game logic.
"""
from pathlib import Path
import random
from util import Direction, HoleTile
from loading import get_board


class Robot:
    def __init__(self, direction, path, path_front, coordinates):
        self.direction = direction
        self.path = path
        self.path_front = path_front
        self.coordinates = coordinates
        self.start_coordinates = coordinates
        self.lives = 3
        self.flags = 0
        self.damages = 9
        self.inactive = False

    def __repr__(self):
        return "<Robot {} {} {} Lives: {} Flags: {} Damages: {}>".format(self.direction, self.path, self.coordinates, self.lives, self.flags, self.damages)

    def walk(self, distance, state, direction=None):
        """
        Move a robot to new coordinates based on its direction.
        Optional argument:
            direction - Default value is set to robot's direction.

        When robot walks, it can move other robots in the way.
        """
        if direction is None:
            direction = self.direction
        for step in range(distance):
            if not self.inactive:
                # Check walls before moving.
                print(self.coordinates)
                wall_check = check_wall(self.coordinates, direction, state)
                if wall_check:
                    # There is no wall. Get new coordinates.
                    next_coordinates = get_next_coordinates(self.coordinates, direction)
                    # Check robots on the next tile.
                    robot_in_the_way = None
                    for robot in state.robots:
                        if robot.coordinates == next_coordinates:
                            # Save index of robot that is in the way.
                            robot_in_the_way = state.robots.index(robot)
                            break
                    # Move robot in the way.
                    if robot_in_the_way is not None:
                            state.robots[robot_in_the_way].walk(1, state, direction)
                            # Check that robot moved.
                            if state.robots[robot_in_the_way].coordinates != next_coordinates:
                                # Robot walks to new coordinates.
                                self.coordinates = next_coordinates
                                # Check hole on new coordinates.
                                for tile in state.get_tiles(self.coordinates):
                                    if not self.inactive:
                                        tile.kill_robot(self)
                                if self.inactive:
                                    break
                    # There isn't a robot in the way. Robot walks to new coordinates.
                    else:
                        self.coordinates = next_coordinates
                        # Check hole on new coordinates.
                        for tile in state.get_tiles(self.coordinates):
                            if not self.inactive:
                                tile.kill_robot(self)
                else:
                    break

    def move(self, direction, distance, state):
        """
        Move a robot to new coordinates according to direction of the move.

        When robot is moved by game elements (convoyer belt or pusher),
        it doesn't have enough power to push other robots. If there is a robot
        in the way, the movement is stopped.
        """
        for step in range(distance):
            # Check walls before moving.
            wall_check = check_wall(self.coordinates, direction, state)
            if wall_check:
                # There is no wall. Get new coordinates.
                next_coordinates = get_next_coordinates(self.coordinates, direction)
                # Check robots on the next tile before moving.
                robot_check = True
                for robot in state.robots:
                    if robot.coordinates == next_coordinates:
                        # There is a robot on the next tile.
                        # Robot can't be moved.
                        robot_check = False
                        break
                # There isn't a robot on the next tile. Robot will be moved.
                if robot_check:
                    self.coordinates = next_coordinates
                    # Check hole on new coordinates.
                    for tile in state.get_tiles(self.coordinates):
                        if not self.inactive:
                            tile.kill_robot(self)
            else:
                break

    def die(self):
        """
        Robot lose life and skip rest of game round.
        Robot is moved out of game board for the rest of the round.
        """
        self.lives -= 1
        # Notification of robot's death during the game round.
        self.inactive = True
        self.coordinates = [-1, -1]

    def rotate(self, where_to):
        """
        Rotate robot according to a given direction.
        """

        self.direction = self.direction.get_new_direction(where_to)


class State:
    def __init__(self, board, robots, sizes):
        self._board = board
        self.robots = robots
        self.sizes = sizes
        self.game_round = 1

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
            return [HoleTile(Direction.N, None, [])]


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


def get_robots_to_start(board):
    """
    Place robots on starting tiles.

    board: dictionary returned by get_board()

    Return list of robots on the starting tiles of the board.

    Initialize Robot objects on the starting tiles coordinates with random
    choice of robot's avatar on particular tile.
    Once the robot is randomly chosen, it is removed from the list
    (it cannot appear twice on the board).
    On the beginning all the Robot objects have implicit 0 degree direction.
    """
    starting_coordinates = get_starting_coordinates(board)
    robot_paths = get_robot_paths()
    robots_start = []
    for coordinate in starting_coordinates:

        # Condition to assure no exception in case robot_paths is shorter
        # than coordinate's list
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

    Create board and robots on starting squares, initialize State object containing Tile and Robot object as well as the map size.
    Return State object.
    """
    board = get_board(map_name)
    tile_count = get_tile_count(board)
    robots_start = get_robots_to_start(board)
    state = State(board, robots_start, tile_count)
    return state


def check_wall(coordinates, direction, state):
    """
    Check wall in the direction of the move.

    coordinates: tuple of x and y coordinate
    direction: object of Direction class
    state: object of State class

    Return a boolean.

    True - There isn't wall, robot can move.
    False - There is wall, robot can't move.
    """
    old_tiles = state.get_tiles(coordinates)
    # On the current tile: Check wall in the direction of next move.
    for tile in old_tiles:
        move_from = tile.can_move_from(direction)
        if not move_from:
            # On the current tile: There is a wall in the direction of the move.
            return False
    if move_from:
        # There is no wall, so get new coordinates.
        next_coordinates = get_next_coordinates(coordinates, direction)
        # Get new list of tiles
        new_tiles = state.get_tiles(next_coordinates)
        # Check wall on the next tile in the direction of the move.
        for tile in new_tiles:
            move_to = tile.can_move_to(direction)
            if not move_to:
                # On the next tile: There is a wall in the direction
                # of the move.
                return False
        if move_to:
            return True


def get_next_coordinates(coordinates, direction):
    """
    Get next coordinates in the given direction from current coordinates.
    """
    (x, y) = coordinates
    (new_x, new_y) = direction.coor_delta
    x = x + new_x
    y = y + new_y
    return (x, y)


def apply_tile_effects(state):
    """
    Apply tile effects according to game rules.
    """
    # Activate belts
        # 1) Express belts move 1 space
        # 2) Express belts and normal belts move 1 space

    # Activate pusher
    for robot in state.robots:
        if not robot.inactive:
            tiles = state.get_tiles(robot.coordinates)
            for tile in tiles:
                # Kill robot if it is standing on hole tile.
                # After completed cards play part with integration of robot
                # dying after card movement. This line can be deleted.
                tile.kill_robot(robot)
                # All set. Start moving.
                tile.push_robot(robot, state)
                if robot.inactive:
                    break

    # Activate gear
    for robot in state.robots:
        if not robot.inactive:
            tiles = state.get_tiles(robot.coordinates)
            for tile in tiles:
                tile.rotate_robot(robot)

    # Activate laser
    for robot in state.robots:
        if not robot.inactive:
            tiles = state.get_tiles(robot.coordinates)
            for tile in tiles:
                tile.shoot_robot(robot, state)
                if robot.inactive:
                    break
    # Activate robot laser

    # Collect flags, repair robots
    for robot in state.robots:
        if not robot.inactive:
            tiles = state.get_tiles(robot.coordinates)
            for tile in tiles:
                tile.collect_flag(robot)
                tile.repair_robot(robot)

    # Delete robots with zero lives
    state.robots = [robot for robot in state.robots if robot.lives > 0]
    for robot in state.robots:
        # If robot lost life during game round, it will now ressurect at its
        # starting coordinates.
        if robot.inactive:
            robot.coordinates = robot.start_coordinates
            robot.damages = 0
            robot.direction = Direction.N
            robot.inactive = False
