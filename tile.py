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

    def kill_robot(self, robot):
        """
        Take away one robot life, set him to inactive mode and move him
        to coordinates for inactive robots (None).

        Take and return Robot class.
        """
        return robot

    def move_robot(self, robot, state):
        return robot

    def push_robot(self, robot, state):
        """
        Move robot by one tile during a specific register phase.

        Return Robot class.
        """
        return robot

    def rotate_robot(self, robot):
        """
        Rotate robot by 90° to the left or right according to tile properties.

        Take and return Robot class.
        """
        return robot

    def shoot_robot(self, robot, state):
        """
        Shoot robot with tile laser.

        robot: Robot class
        state: State class

        Return Robot class.
        """
        return robot

    def collect_flag(self, robot):
        """
        Collect flag by robot and change robot's start coordinates.

        Take and return Robot class.
        """
        return robot

    def repair_robot(self, robot, state):
        """
        Repair one robot's damage. Change robot's start coordinates, if possible by tile properties.

        robot: Robot class
        state: State class

        Return Robot class.
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
    # Start tile has no tile effect.
    def __init__(self, direction, path, properties):
        self.number = properties[0]["value"]
        super().__init__(direction, path, properties)



class HoleTile(Tile):
    def __init__(self, direction=Direction.N, path=None, properties=[]):
        super().__init__(direction, path, properties)

    def kill_robot(self, robot):
        # Call robot's method for dying.
        return robot.die()


class BeltTile(Tile):
    def __init__(self, direction, path, properties):
        self.crossroads = properties[0]["value"]
        self.belt_direction = properties[1]["value"]
        self.move_count = properties[2]["value"]
        super().__init__(direction, path, properties)

    def move_robot(self, state):
        # TO DO!

        # 1) Express belts move 1 space
        # 2) Express belts and normal belts move 1 space
        pass


class PusherTile(Tile):
    def __init__(self, direction, path, properties):
        self.register = properties[0]["value"]
        super().__init__(direction, path, properties)

    def push_robot(self, robot, state):
        # Check register and activate correct pushers.
        # PusherTile property register:
        #  0 for even register number,
        #  1 for odd register number.
        if state.register % 2 == self.register:
            robot.move(self.direction.get_new_direction(Rotation.U_TURN), 1, state)


class GearTile(Tile):
    def __init__(self, direction, path, properties):
        self.move_direction = transform_direction(properties[0]["value"])
        super().__init__(direction, path, properties)

    def rotate_robot(self, robot):
        # Rotate robot by 90° according to GearTile property: left or right.
        robot.rotate(self.move_direction)

class LaserTile(Tile):
    def __init__(self, direction, path, properties):
        self.laser_strength = properties[0]["value"]
        self.laser_start = properties[1]["value"]
        super().__init__(direction, path, properties)

    def shoot_robot(self, robot, state):
        # Robot stands on laser tile.
        hit = True
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
            while hit:
                # Get new coordinates.
                (x, y) = get_next_coordinates((x, y), direction_to_start)
                # Check for other robots.
                if (x, y) in coordinates:
                    # There is another robot.
                    # Current robot won't be hit by laser.
                    hit = False
                    break
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
        if hit:
            robot.be_damaged(self.laser_strength)


class FlagTile(Tile):
    def __init__(self, direction, path, properties):
        self.flag_number = properties[0]["value"]
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
        self.new_start = properties[0]["value"]
        super().__init__(direction, path, properties)

    def repair_robot(self, robot, state):
        if state.register == 5:
            # Remove one robot damage.
            if robot.damages > 0:
                robot.damages -= 1
        # Change start coordinates of robot, if it's a tile property.
        if self.new_start:
            robot.start_coordinates = robot.coordinates


TILE_CLS = {'wall': WallTile, 'start_square': StartTile, 'hole': HoleTile,
            'laser': LaserTile, 'gear': GearTile, 'pusher': PusherTile,
            'belt': BeltTile, 'flag': FlagTile, 'repair': RepairTile,
            'ground': Tile}


def create_tile_subclass(direction, path, type, properties):
    """
    Create tile subclass according to its type.
    """
    return TILE_CLS[type](direction, path, properties)


def transform_direction(direction_int):
    """
    Function to transform the string taken from json properties to valid Rotation class instance for later processing.
    """
    if direction_int == -1:
        return Rotation.LEFT
    if direction_int == 1:
        return Rotation.RIGHT
