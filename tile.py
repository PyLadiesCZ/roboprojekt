"""
Tile contains class Tile and its subclasses.
"""

from util import Direction, Rotation, get_next_coordinates


class Tile:
    def __init__(self, direction, path, properties):
        self.direction = direction
        self.path = path

    def __repr__(self):
        # type(self).__name__: shows the type of the particular tile
        # eg. HoleTile, WallTile or just Tile
        return "<{} {}>".format(type(self).__name__, self.direction)

    def can_move_from(self, direction):
        """
        Verify movement from tile in specific direction.

        Return a boolean.

        True - There is not a wall in direction of the move.
        False - There is a wall in direction of the move.
        """
        return True

    def can_move_to(self, direction):
        """
        Verify movement to tile from specific direction.

        Return a boolean.

        True - There is not a wall in direction of the move.
        False - There is a wall in direction of the move.
        """
        return True

    def properties_dict(self, coordinate):
        """
        Create a dictionary of properties (coordinates and direction).

        For StartTile return a dictionary.
        For other tiles return None.
        """
        return None

    def stop_properties_dict(self, coordinate):
        """
        Create a dictionary of properties (coordinates and direction).

        For StopTile return a dictionary.
        For other tiles return None.
        """
        return None

    def kill_robot(self, robot):
        """
        Take away one robot life, set him to inactive mode
        and set his coordinates to None.
        """
        return robot

    def check_belts(self, express_belts):
        """
        Check that current tile is conveyor belt of desired type.
        express_belts: a boolean, True for express belts, False for all belts.
        Return a boolean.
        True - Tile is conveyor belt of desired type.
        False - Tile isn't conveyor belt or it's a wrong type of belt.
        """
        return False

    def rotate_robot_on_belt(self, robot, direction):
        """
        Rotate robot on rotating conveyor belts. If robot's rotated,
        will be decided by the direction he entered a tile.
        direction: direction from which robot entered a tile
        """
        return robot

    def push_robot(self, robot, state, round):
        """
        Move robot by one tile during a specific register phase.
        """
        return robot

    def rotate_robot(self, robot):
        """
        Rotate robot by 90° to the left or right according to tile properties.
        """
        return robot

    def shoot_robot(self, robot, state):
        """
        Shoot robot with tile laser. Number of robot's damages is raised by
        the strength of laser. If the new number of damages is greater than 9,
        robot is killed.
        """
        return robot

    def collect_flag(self, robot):
        """
        Collect flag by robot and change robot's start coordinates.
        """
        return robot

    def repair_robot(self, robot, state, round):
        """
        Repair one robot's damage. Change robot's start coordinates,
        if possible by tile properties.
        """
        return robot


class WallTile(Tile):
    def can_move_from(self, direction):
        # The direction of the wall is the same as the direction in which
        # robot wants to move from the tile.
        return not (self.direction == direction)

    def can_move_to(self, direction):
        # If there is a wall in direction of the robot movement,
        # then the direction of the robot goes against the direction of the wall.
        # Because of that the tile is checked in upside down direction.
        return not (self.direction.get_new_direction(Rotation.U_TURN) == direction)


class StartTile(Tile):
    def __init__(self, direction, path, properties):
        self.number = properties["number"]
        super().__init__(direction, path, properties)

    def properties_dict(self, coordinate):
        return {"coordinates": coordinate, "tile_direction": self.direction}


class StopTile(Tile):
    def __init__(self, direction, path, properties):
        self.number = properties["number"]
        super().__init__(direction, path, properties)

    def stop_properties_dict(self, coordinate):
        return {"coordinates": coordinate, "tile_direction": self.direction}


class HoleTile(Tile):
    def __init__(self, direction=Direction.N, path=None, properties={}):
        super().__init__(direction, path, properties)

    def kill_robot(self, robot):
        # Call robot's method for dying.
        return robot.die()


class BeltTile(Tile):
    def __init__(self, direction, path, properties):
        self.direction_out = transform_direction(properties["direction_out"])
        self.express = properties["express"]
        super().__init__(direction, path, properties)

    def check_belts(self, express_belts):
        # Only express belts
        if self.express is express_belts:
            return True
        # All belts
        elif express_belts is False:
            return True
        else:
            return False

    def rotate_robot_on_belt(self, robot, direction):
        # Special condition for one type of crossroads:
        # If crossroads have Direction.N, then the special type has exit
        # on south part of tile.
        if self.direction_out == Rotation.U_TURN:
            if self.direction.get_new_direction(Rotation.RIGHT) == direction:
                robot.rotate(Rotation.RIGHT)
            else:
                robot.rotate(Rotation.LEFT)
        # All other rotating belts or crossroads.
        elif isinstance(self.direction_out, Rotation):
                if direction == self.direction:
                    robot.rotate(self.direction_out)


class PusherTile(Tile):
    def __init__(self, direction, path, properties):
        self.register = properties["register"]
        super().__init__(direction, path, properties)

    def push_robot(self, robot, state, round):
        # Check register and activate correct pushers.
        # PusherTile property register:
        #  0 for even register number,
        #  1 for odd register number.
        if (round + 1) % 2 == self.register:
            robot.move(self.direction.get_new_direction(Rotation.U_TURN), 1, state)


class GearTile(Tile):
    def __init__(self, direction, path, properties):
        self.move_direction = transform_direction(properties["move_direction"])
        super().__init__(direction, path, properties)

    def rotate_robot(self, robot):
        # Rotate robot by 90° according to GearTile property: left or right.
        robot.rotate(self.move_direction)


class LaserTile(Tile):
    def __init__(self, direction, path, properties):
        self.laser_strength = properties["laser_strength"]
        self.laser_start = properties["laser_start"]
        super().__init__(direction, path, properties)

    def shoot_robot(self, robot, state):
        # Robot stands on laser tile.
        # If robot isn't standing on the start of the laser, look for other robots.
        if not self.laser_start:
            # Get coordinates of current robot.
            (x, y) = robot.coordinates
            # Get coordinates of other robots.
            coordinates = []
            for robot_state in state.robots:
                coordinates.append(robot_state.coordinates)
            # Get direction in which it will be checked for other robots or laser start.
            direction_to_start = self.direction.get_new_direction(Rotation.U_TURN)
            # Check if there is another robot in direction of incoming laser.
            while True:
                # Get new coordinates.
                (x, y) = get_next_coordinates((x, y), direction_to_start)
                # Check for other robots.
                if (x, y) in coordinates:
                    # There is another robot.
                    # Current robot won't be hit by laser.
                    return
                # Get new tiles.
                new_tiles = state.get_tiles((x, y))
                for tile in new_tiles:
                    # Check if new tiles contain follow-up LaserTile in correct direction.
                    if isinstance(tile, LaserTile) and tile.direction == self.direction:
                        # Follow-up laser tile found, don't check ohter tiles here.
                        break
                # Check for laser start tile.
                if isinstance(tile, LaserTile) and tile.laser_start:
                    # Don't check new tiles.
                    break
        robot.be_damaged(self.laser_strength)


class FlagTile(Tile):
    def __init__(self, direction, path, properties):
        self.flag_number = properties["flag_number"]
        super().__init__(direction, path, properties)

    def collect_flag(self, robot):
        # Robot always changes his start coordinates, when he is on a flag.
        # Flag number doesn't play a role.
        robot.start_coordinates = robot.coordinates
        # Collect only correct flag.
        # Correct flag will have a number that is equal to robot's flag number plus one.
        if (robot.flags + 1) == self.flag_number:
            robot.flags += 1


class RepairTile(Tile):
    def __init__(self, direction, path, properties):
        self.new_start = properties["new_start"]
        super().__init__(direction, path, properties)

    def repair_robot(self, robot, state, round):
        if (round + 1) == 5:
            # Remove one robot damage.
            if robot.damages > 0:
                robot.damages -= 1
        # Change start coordinates of robot, if it's a tile property.
        if self.new_start:
            robot.start_coordinates = robot.coordinates


TILE_CLS = {'wall': WallTile, 'start': StartTile, 'hole': HoleTile,
            'laser': LaserTile, 'gear': GearTile, 'pusher': PusherTile,
            'belt': BeltTile, 'flag': FlagTile, 'repair': RepairTile,
            'ground': Tile, 'stop': StopTile}


def create_tile_subclass(direction, path, type, properties):
    """
    Create tile subclass according to its type.
    """
    return TILE_CLS[type](direction, path, properties)


def transform_direction(direction_int):
    """
    Function to transform the string taken from json properties to valid
    Rotation class instance for later processing.
    """
    if direction_int == 0:
        return Direction.N
    if direction_int == -1:
        return Rotation.LEFT
    if direction_int == 1:
        return Rotation.RIGHT
    if direction_int == 2:
        return Rotation.U_TURN
