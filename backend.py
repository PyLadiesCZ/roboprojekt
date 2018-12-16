"""
Backend file contains functions for the game logic.
"""
from pathlib import Path
import random
from util import Tile, Direction
from loading import get_board


class Robot:
    def __init__(self, direction, path, coordinates):
        self.direction = direction
        self.path = path
        self.coordinates = coordinates
        self.lifecount = 3
        self.flagcount = 0
        self.damagecount = 0

    def __repr__(self):
        return "<Robot {} {} {} Lifes: {} Flags: {} Damages: {}>".format(self.direction, self.path, self.coordinates, self.lifecount, self.flagcount, self.damagecount)

    def walk(self, distance, state):
        """
        Move a robot to new coordinates based on its direction.
        """
        self.move(self.direction, distance, state)

    def move(self, direction, distance, state):
        """
        Move a robot to new coordinates according to direction of the move.
        """
        for step in range(distance):
            old_tiles = state.board[self.coordinates]
            # On the current tile: Check wall in the direction of next move.
            for tile in old_tiles:
                move_from = tile.can_move_from(direction)
                if move_from is False:
                    break
            if move_from:
                # There is no wall, so get new coordinates.
                (x, y) = self.coordinates
                (new_x, new_y) = direction.coor_delta
                x = x + new_x
                y = y + new_y
                new_tiles = state.board[(x, y)]
                # Check wall on the next tile in the direction of the move.
                for tile in new_tiles:
                    move_to = tile.can_move_to(direction)
                    if move_to is False:
                        break
                if move_to:
                    self.coordinates = (x, y)
                else:
                    # On the next tile: There is a wall in the direction
                    # of the move.
                    # Coordinates won't be changed. Break the loop, don't check
                    # these tiles again.
                    break
            else:
                # On the current tile: There is a wall in the direction
                # of the move.
                # Break the loop, don't check next tile.
                break

    def rotate(self, where_to):
        """
        Rotate robot according to a given direction.
        """

        self.direction = self.direction.get_new_direction(where_to)


class State:
    def __init__(self, board, robots, sizes):
        self.board = board
        self.robots = robots
        self.sizes = sizes

    def __repr__(self):
        return "<State {} {}>".format(self.board, self.robots)



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
        robot_paths.append(robot_path)
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
            path = random.choice(robot_paths)
            robot_paths.remove(path)
            robot = Robot(Direction.N, path, coordinate)
            robots_start.append(robot)
    return robots_start


def get_start_state(map_name):
    """
    Get starting state of game.

    data: a dict created from decoded Tiled 1.2 JSON file

    Create board and robots on starting squares, initialize State object containing both Tile and Robot object.
    Return State object.
    """
    #sizes = [data["width"], data["height"]]
    board, map_size = get_board(map_name)
    robots_start = get_robots_to_start(board)
    state = State(board, robots_start, map_size)
    return state
