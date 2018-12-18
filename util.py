"""
Util contains classes Tile and Direction, accessed by both loading and backend.
"""

from enum import Enum


class Tile:
    def __init__(self, direction, path, type):
        self.direction = direction
        self.path = path
        self.type = type

    def __repr__(self):
        return "<Tile {} {}>".format(self.direction, self.type)

    def can_move_from(self, direction):
        """
        Verify movement from tile in specific direction.

        Return a boolean.

        True - There is not a wall in direction of the move.
        False - There is a wall in direction of the move.
        """
        # The direction of the wall is the same as the direction in which
        # robot wants to move from the tile.
        if (self.type == "wall" and self.direction == direction):
            return False
        else:
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
        if (self.type == "wall" and self.direction.get_new_direction("upside_down") == direction):
            return False
        else:
            return True


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
