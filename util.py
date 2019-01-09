"""
Util contains classes Tile and Direction, accessed by both loading and backend.
"""

from enum import Enum


class Tile:
    def __init__(self, direction, path, properties):
        self.direction = direction
        self.path = path

    def __repr__(self):
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
        # If there is a wall in direction of the robot movement,
        # than the direction of the robot goes against the direction of the wall.
        # Because of that the tile is rotate upside down.
        return True

    def kill_robot(self, robot):
        """
        Take away one robot life or kill robot.

        Take and return Robot class.
        """
        return robot

    def move_robot(self, robot, state):
        return robot

    def push_robot(self, robot, state):
        """
        Move robot by one tile in specific game round.

        robot: Robot class
        state: State class containing game round

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

    def repair_robot(self, robot):
        """
        Repair robot. Change robot's start coordinates, if possible by tile properties.

        Take and return Robot class.
        """
        return robot


class WallTile(Tile):
    def can_move_from(self, direction):
        # The direction of the wall is the same as the direction in which
        # robot wants to move from the tile.
        return not (self.direction == direction)

    def can_move_to(self, direction):
        # If there is a wall in direction of the robot movement,
        # than the direction of the robot goes against the direction of the wall.
        # Because of that the tile is rotate upside down.
        return not (self.direction.get_new_direction("upside_down") == direction)


class StartTile(Tile):
    # Start tile has no tile effect.
    pass


class HoleTile(Tile):
    def kill_robot(self, robot):
        # Call robot's method for dying
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
        self.game_round = properties[0]["value"]
        super().__init__(direction, path, properties)

    def push_robot(self, robot, state):
        # Check game round and activate correct pushers.
        # PusherTile property game_round:
        #  0 for even game round number,
        #  1 for odd game round number.
        if state.game_round % 2 and self.game_round:
            # Pusher for even game rounds.
            robot.move(self.direction.get_new_direction("upside_down"), 1, state)
        elif state.game_round % 2 == self.game_round:
            # Pusher for odd game rounds.
            robot.move(self.direction.get_new_direction("upside_down"), 1, state)
        # Check hole on the next coordinates.
        tiles = state.get_tiles(robot.coordinates)
        for tile in tiles:
            tile.kill_robot(robot)


class GearTile(Tile):
    def __init__(self, direction, path, properties):
        self.move_direction = properties[0]["value"]
        super().__init__(direction, path, properties)

    def rotate_robot(self, robot):
        # Rotate robot by 90° according to GearTile property: left or right.
        robot.direction = robot.direction.get_new_direction(self.move_direction)


class LaserTile(Tile):
    def __init__(self, direction, path, properties):
        self.laser_number = properties[0]["value"]
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
            direction_to_start = self.direction.get_new_direction('upside_down')
            # Check if there is another robot in direction of incoming laser.
            while hit:
                # Get new coordinates and new tiles.
                (new_x, new_y) = direction_to_start.coor_delta
                x = x + new_x
                y = y + new_y
                new_tiles = state.get_tiles((x, y))
                for tile in new_tiles:
                    # Check if new tiles contain follow-up LaserTile in correct direction.
                    if isinstance(tile, LaserTile) and tile.direction == self.direction:
                        # Check for other robots.
                        if (x, y) in coordinates:
                            # There is another robot.
                            # Current robot won't be hit by laser.
                            hit = False
                            break
                        elif tile.laser_start:
                            # There is no other robot and laser starts here.
                            # Current robot will be hit by laser.
                            break
                        else:
                            # Laser continues, check another set of tiles.
                            break
                if isinstance(tile, LaserTile):
                    # Check for laser start tile.
                    if tile.laser_start:
                        # Don't check other tiles.
                        break
        if hit:
            # No robots found in the direction of incoming laser.
            # So do damage to robot.
            if robot.damages < (10 - self.laser_number):
                # Laser won't kill robot, but it will damage robot.
                robot.damages += self.laser_number
            else:
                # Robot is damaged so much, that laser kills it.
                robot.die()


class FlagTile(Tile):
    def __init__(self, direction, path, properties):
        self.flag_number = properties[0]["value"]
        super().__init__(direction, path, properties)

    def collect_flag(self, robot):
        # Collect only correct flag.
        # Correct flag will have a number that is equal to robot flag number plus one.
        if (robot.flags + 1) == self.flag_number:
            # Flag collected and start coordinates changed to flag's coordinates.
            robot.flags += 1
            robot.start_coordinates = robot.coordinates


class RepairTile(Tile):
    def __init__(self, direction, path, properties):
        self.new_start = properties[0]["value"]
        super().__init__(direction, path, properties)

    def repair_robot(self, robot):
        # Remove one robot damage.
        if robot.damages > 0:
            robot.damages -= 1
        # Change starting coordinates of robot, if it's a tile property.
        if self.new_start:
            robot.start_coordinates = robot.coordinates


class Direction(Enum):
    N = 0, (0, +1), 0
    E = 90, (+1, 0), 1
    S = 180, (0, -1), 2
    W = 270, (-1, 0), 3

    def __new__(cls, degrees, coor_delta, tile_property):
        """
        Get attributes value and vector of the given Direction class values.

        Override standard enum __new__ method.
        vector: new coordinates (where the robot goes to)
        tile_property: map tile property: value (custom - added in Tiled).
        Makes it possible to change vector and tile_property when the object is rotated.
        With degrees change (value) there comes the coordinates (vector) change and tile_property.

        More info about enum - official documentation: https://docs.python.org/3/library/enum.html
        Blog post with the exact __new__() usage: http://xion.io/post/code/python-enums-are-ok.html
        """
        obj = object.__new__(cls)
        obj._value_ = degrees
        obj.coor_delta = coor_delta
        obj.map_property = tile_property
        return obj

    def get_new_direction(self, where_to):
        """
        Get new direction of given object.

        Change attribute direction according to argument where_to, passed from TDB class DirectionOfRotation.
        """
        if where_to == "right":
            return Direction((self.value + 90) % 360)
        if where_to == "left":
            return Direction((self.value + 270) % 360)
        if where_to == "upside_down":
            return Direction((self.value + 180) % 360)


def tile_factory(direction, path, type, properties):
    """
    Select tile subclass according to its type and create coressponding subclass.
    """
    return tile_cls[type](direction, path, properties)


tile_cls = {'wall': WallTile, 'starting_square': StartTile, 'hole': HoleTile,
            'laser': LaserTile, 'gear': GearTile, 'pusher': PusherTile,
            'belt': BeltTile, 'flag': FlagTile, 'repair': RepairTile,
            'ground': Tile}
