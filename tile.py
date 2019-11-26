"""
Tile contains class Tile and its subclasses.
"""

from util_backend import Direction, Rotation, get_next_coordinates


class Tile:
    def __init__(self, direction, name, tile_type, properties):
        self.direction = direction
        self.name = name
        self.type = tile_type

    def __eq__(self, other):
        """
        Override standard method for comparing the tiles.
        When tile has the same name and direction as the other, it is
        considered the same.
        """
        if (self.name == other.name) and (self.direction == other.direction):
            return True

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

    def kill_robot(self, state, robot):
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

    def rotate_robot_on_belt(self, robot, direction, state):
        """
        Rotate robot on rotating conveyor belts. If robot's rotated,
        will be decided by the direction he entered a tile.
        direction: direction from which robot entered a tile
        """
        return robot

    def push_robot(self, robot, state, register):
        """
        Move robot by one tile during a specific register phase.
        """
        return False

    def rotate_robot(self, robot, state):
        """
        Rotate robot by 90° to the left or right according to tile properties.
        """
        return False

    def shoot_robot(self, robot, state):
        """
        Shoot robot with tile laser. Number of robot's damages is raised by
        the strength of laser. If the new number of damages is greater than 9,
        robot is killed.
        """
        return False

    def collect_flag(self, robot, state):
        """
        Collect flag by robot and change robot's start coordinates.
        """
        return False

    def repair_robot(self, robot, state):
        """
        Repair one robot's damage.
        """
        return False

    def set_new_start(self, robot, state):
        """
        Change robot's start coordinates, if possible by tile properties.
        """
        return False


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
    def __init__(self, direction, name, tile_type, properties):
        self.number = properties["number"]
        super().__init__(direction, name, tile_type, properties)


class StopTile(Tile):
    def __init__(self, direction, name, tile_type, properties):
        self.number = properties["number"]
        super().__init__(direction, name, tile_type, properties)


class HoleTile(Tile):
    def __init__(self, direction=Direction.N, name=None, tile_type=None, properties={}):
        super().__init__(direction, name, tile_type, properties)

    def kill_robot(self, state, robot):
        # Call robot's method for dying.
        robot.die(state)
        return robot

class BeltTile(Tile):
    def __init__(self, direction, name, tile_type, properties):
        if properties["direction_out"] == 0:
            self.direction_out = Direction.N
        else:
            self.direction_out = Rotation(properties["direction_out"])
        self.express = properties["express"]
        super().__init__(direction, name, tile_type, properties)

    def check_belts(self, express_belts):
        # Only express belts
        if self.express is express_belts:
            return True
        # All belts
        elif express_belts is False:
            return True
        else:
            return False

    def rotate_robot_on_belt(self, robot, direction, state):
        # Special condition for one type of crossroads:
        # If crossroads have Direction.N, then the special type has exit
        # on south part of tile.
        if self.direction_out == Rotation.U_TURN:
            if self.direction.get_new_direction(Rotation.RIGHT) == direction:
                robot.rotate(Rotation.RIGHT, state)
            else:
                robot.rotate(Rotation.LEFT, state)
        # All other rotating belts or crossroads.
        elif isinstance(self.direction_out, Rotation):
                if direction == self.direction:
                    robot.rotate(self.direction_out, state)


class PusherTile(Tile):
    def __init__(self, direction, name, tile_type, properties):
        self.register = properties["register"]
        super().__init__(direction, name, tile_type, properties)

    def push_robot(self, robot, state, register):
        # Check register and activate correct pushers.
        # PusherTile property register:
        #  0 for even register number,
        #  1 for odd register number.
        if (register + 1) % 2 == self.register:
            robot.move(self.direction.get_new_direction(Rotation.U_TURN), 1, state)
            return True

class GearTile(Tile):
    def __init__(self, direction, name, tile_type, properties):
        self.move_direction = Rotation(properties["move_direction"])
        super().__init__(direction, name, tile_type, properties)

    def rotate_robot(self, robot, state):
        # Rotate robot by 90° according to GearTile property: left or right.
        robot.rotate(self.move_direction, state)
        return True


class LaserTile(Tile):
    def __init__(self, direction, name, tile_type, properties):
        self.laser_strength = properties["laser_strength"]
        self.start = properties["start"]
        super().__init__(direction, name, tile_type, properties)

    def shoot_robot(self, robot, state):
        # Robot stands on laser tile.
        # If robot isn't standing on the start of the laser, look for other robots.
        if not self.start:
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
                if tile.start:
                    # Don't check new tiles.
                    break
        robot.be_damaged(state, self.laser_strength)
        return True


class FlagTile(Tile):
    def __init__(self, direction, name, tile_type, properties):
        self.number = properties["number"]
        super().__init__(direction, name, tile_type, properties)

    def collect_flag(self, robot, state):
        # Robot always changes his start coordinates, when he is on a flag.
        # Flag number doesn't play a role.
        robot.change_start_coordinates(state)
        # Collect only correct flag.
        # Correct flag will have a number that is equal to robot's flag number plus one.
        if (robot.flags + 1) == self.number:
            robot.flags += 1
        return True


class RepairTile(Tile):
    def __init__(self, direction, name, tile_type, properties):
        self.new_start = properties["new_start"]
        super().__init__(direction, name, tile_type, properties)

    def repair_robot(self, robot, state):
        # Remove one robot damage.
        if robot.damages > 0:
            robot.damages -= 1
            state.record_log()
            return True

    def set_new_start(self, robot, state):
        # Change start coordinates of robot, if it's a tile property.
        if self.new_start:
            robot.change_start_coordinates(state)
            return True


TILE_CLS = {'wall': WallTile, 'start': StartTile, 'hole': HoleTile,
            'laser': LaserTile, 'gear': GearTile, 'pusher': PusherTile,
            'belt': BeltTile, 'flag': FlagTile, 'repair': RepairTile,
            'ground': Tile, 'stop': StopTile}


def create_tile_subclass(direction, name, tile_type, properties):
    """
    Create tile subclass according to its tile_type.
    """
    return TILE_CLS[tile_type](direction, name, tile_type, properties)
