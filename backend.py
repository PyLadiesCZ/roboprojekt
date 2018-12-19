"""
Backend file contains functions for the game logic.
"""
from pathlib import Path
import random
from util import Tile, Direction, HoleTile
from loading import get_board


class Robot:
    def __init__(self, direction, path, path_front, coordinates):
        self.direction = direction
        self.path = path
        self.path_front = path_front
        self.coordinates = coordinates
        self.start_coordinates = coordinates
        self.lifes = 3
        self.flags = 0
        self.damages = 8
        self.power_down = False

    def __repr__(self):
        return "<Robot {} {} {} Lifes: {} Flags: {} Damages: {}>".format(self.direction, self.path, self.coordinates, self.lifes, self.flags, self.damages)

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
            old_tiles = state.get_tiles(self.coordinates)
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
                # When the robot leaves the map, robot dies
                new_tiles = state.get_tiles((x, y))
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

    def die(self):
        self.lifes -= 1
        # Check number of robot lifes.
        if self.lifes > 1:
            # Robot has 2 or more lifes, so it can ressurect at its starting coordinates.
            self.damages = 0
            self.coordinates = self.start_coordinates
            self.direction = Direction.N
        # else:
            # odebrat robota ze seznamu
            # Robot has only one life, so it dies.

        return True

    def rotate(self, where_to):
        """
        Rotate robot according to a given direction.
        """

        self.direction = self.direction.get_new_direction(where_to)

    def apply_tile_effects(self, state):
        tiles = state.get_tiles(self.coordinates)
        for tile in tiles:
            # První budou efekty pohybu:
            # 1) Dvojité šipky udělají jeden krok
            # 2) Jednoduché šipky + dvojité šipky udělají jeden krok
            # 3) Aktivují se pushery
            # 4) Aktivují se geary - otočení robota o 90°
            tile.move_robot(self, state)  # TO DO!
            tile.push_robot(self, state)
            tile.rotate_robot(self)
            if tile.kill_robot(self):
                break

            # Aktivace laserů:
            # 1) Lasery políček
            # 2) Lasery robotů - # TO DO!
            if tile.shoot_robot(self, state):
                # True if robot shoot to death
                break
            # Sbírání vlajek a opravy robotů
            tile.collect_flag(self)
            tile.repair_robot(self)


class State:
    def __init__(self, board, robots, sizes):
        self._board = board
        self.robots = robots
        self.sizes = sizes
        self.game_round = 1

    def __repr__(self):
        return "<State {} {}>".format(self._board, self.robots)

    def get_tiles(self, coordinates):
        if coordinates in self._board:
            return self._board[coordinates]
        else:
            return [HoleTile(Direction.N, None)]


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

    data: a dict created from decoded Tiled 1.2 JSON file

    Create board and robots on starting squares, initialize State object containing both Tile and Robot object.
    Return State object.
    """
    board = get_board(map_name)
    tile_count = get_tile_count(board)
    robots_start = get_robots_to_start(board)
    state = State(board, robots_start, tile_count)
    return state
