"""
Util contains classes Direction and Rotation, accessed by both loading and backend.
"""

from enum import Enum


class Direction(Enum):
    N = 0, (0, +1)
    E = 90, (+1, 0)
    S = 180, (0, -1)
    W = 270, (-1, 0)

    def __new__(cls, degrees, coor_delta):
        """
        Get attributes value and vector of the given Direction class values.

        Override standard enum __new__ method.
        coor_delta: new coordinates (where the robot goes to)
        tile_property: map tile property: value (custom - added in Tiled).
        Makes it possible to change delta and tile_property
        when the object is rotated.

        More info about enum - official documentation:
        https://docs.python.org/3/library/enum.html
        Blog post with the exact __new__() usage:
        http://xion.io/post/code/python-enums-are-ok.html
        """
        obj = object.__new__(cls)
        obj._value_ = degrees
        obj.coor_delta = coor_delta
        return obj

    def __add__(self, other):
        return Direction((self.value + other.value) % 360)

    def get_new_direction(self, where_to):
        """
        Get new direction of given object.
        Change attribute direction according to argument where_to,
        passed from class Rotation.
        """
        return Direction(self + where_to)


class Rotation(Enum):
    """
    Class describing the direction of the movement of the object-robot (dynamic).
    """
    LEFT = -90
    RIGHT = 90
    U_TURN = 180


def get_next_coordinates(coordinates, direction):
    """
    Get next coordinates in the given direction from current coordinates.
    """
    (x, y) = coordinates
    (new_x, new_y) = direction.coor_delta
    x = x + new_x
    y = y + new_y
    return (x, y)
