import pyglet
from contextlib import contextmanager
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


def get_sprite(img_path, x=0, y=0):
    """
    Return sprite of image.
    """
    img = pyglet.image.load(img_path)
    return pyglet.sprite.Sprite(img, x, y)


@contextmanager
def window_zoom(window, WINDOW_WIDTH, WINDOW_HEIGHT):
    """
    Contextmanager for zoom of window.
    """
    pyglet.gl.glPushMatrix()
    window.clear()
    zoom = min(
        window.height / WINDOW_HEIGHT,
        window.width / WINDOW_WIDTH
    )
    pyglet.gl.glScalef(zoom, zoom, 1)
    yield
    pyglet.gl.glPopMatrix()
