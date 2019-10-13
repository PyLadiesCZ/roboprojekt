import pyglet
from functools import lru_cache

# Constatnts for size of tile image in px
TILE_WIDTH = 64
TILE_HEIGHT = 64


@lru_cache(maxsize=100)
def get_label(text, x, y, font_size, anchor_x, color):
    """
    Return text label with parameters defined from given arguments.
    Store last 100 labels in cache, documented here:
    https://docs.python.org/3/library/functools.html#functools.lru_cache
    """
    label = pyglet.text.Label()
    label.text = text
    label.x = x
    label.y = y
    label.font_size = font_size
    label.anchor_x = anchor_x
    label.color = color
    return label
