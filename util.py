"""
Util contains classes Tile and Direction, accessed by both loading and backend.
"""

from enum import Enum


class Tile:
    def __init__(self, direction, path):
        self.direction = direction
        self.path = path

    def __repr__(self):
        return "<{} {}>".format(type(self).__name__, self.direction)

    def tile_factory(direction, path, type, properties):
        if type == 'wall':
            return WallTile(direction, path)
        elif type == 'hole':
            return HoleTile(direction, path)
        elif type == 'starting_square':
            return StartTile(direction, path)
        elif type == 'laser':
            return LaserTile(direction, path, properties)
        elif type == 'gear':
            return GearTile(direction, path, properties)
        elif type == 'pusher':
            return PusherTile(direction, path, properties)
        elif type == 'belt':
            return BeltTile(direction, path, properties)
        elif type == 'flag':
            return FlagTile(direction, path, properties)
        elif type == 'repair':
            return RepairTile(direction, path, properties)
        else:
            return Tile(direction, path)
# Wall

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

# Hole
    def kill_robot(self, robot_life_count):
        return robot_life_count

# Starting square

# Laser
    def shoot_robot(self, robot_damage_count):
        return robot_damage_count

# Gear
    def rotate_robot(self, robot_direction):
        return robot_direction

# Pusher
    def push_robot(self, robot_coordinates):
        return robot_coordinates

# Belt
    def move_robot(self, robot_coordinates):
        return robot_coordinates

# Flag
    def collect_flag(self, robot_flag_count):
        return robot_flag_count

# Repair
    def heal_robot(self, robot_damage_count):
        return robot_damage_count


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


class HoleTile(Tile):
    def kill_robot(self, robot_life_count):
        if robot_life_count > 1:
            robot_life_count -= 1


class StartTile(Tile):
    pass


class LaserTile(Tile):
    def __init__(self, direction, path, properties):
        self.laser_start = properties[0]["value"]
        self.laser_number = properties[1]["value"]
        super().__init__(direction, path)

    def shoot_robot(self, state):
        pass


class GearTile(Tile):
    def __init__(self, direction, path, properties):
        self.direction_move = properties[0]["value"]
        super().__init__(direction, path)

    def rotate_robot(self, state):
        pass


class PusherTile(Tile):
    def __init__(self, direction, path, properties):
        self.game_round = properties[0]["value"]
        self.move_count = properties[1]["value"]
        super().__init__(direction, path)

    def push_robot(self, state):
        pass


class BeltTile(Tile):
    def __init__(self, direction, path, properties):
        self.crossroads = properties[0]["value"]
        self.belt_direction = properties[1]["value"]
        self.move_count = properties[2]["value"]
        super().__init__(direction, path)

    def move_robot(self, state):
        pass


class FlagTile(Tile):
    def __init__(self, direction, path, properties):
        self.flag_number = properties[0]["value"]
        super().__init__(direction, path)

    def collect_flag(self, state):
        pass


class RepairTile(Tile):
    def __init__(self, direction, path, properties):
        self.damage_count = properties[0]["value"]
        super().__init__(direction, path)

    def heal_robot(self, robot_damage_count):
        if robot_damage_count > 0:
            robot_damage_count += self.damage_count
        return robot_damage_count


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
