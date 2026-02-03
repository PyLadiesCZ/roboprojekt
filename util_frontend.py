import pyglet
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

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
    pyglet.gl.gl_compat.glPushMatrix()
    window.clear()
    zoom = min(
        window.height / WINDOW_HEIGHT,
        window.width / WINDOW_WIDTH
    )
    pyglet.gl.gl_compat.glScalef(zoom, zoom, 1)
    yield
    pyglet.gl.gl_compat.glPopMatrix()


_init_module_after_gl_context_called = False

def _init_module_after_gl_context():
    """ loads sprites into global variables after a GL context is created. """
    global _init_module_after_gl_context_called
    if _init_module_after_gl_context_called:
        return
    _init_module_after_gl_context_called = True

    # Loading of robots images
    for image_path in Path('./img/robots/png').iterdir():
        loaded_robots_images[image_path.stem] = pyglet.image.load(str(image_path))

    # Create player sprite, use fake image, replaced with the actual one-
    player_sprite_proxy._set_actual_sprite(get_sprite('img/robots/png/bender.png'))

loaded_robots_images = {}  # initialized in init_module_after_gl_context

class PlayerSpriteProxy:
    # player_sprite is used from multiple modules in same running program
    # and cannot be created as None -> a proxy object

    def __init__(self):
        self.__dict__['_actual_sprite'] = None

    def _set_actual_sprite(self, actual_sprite):
        self._actual_sprite = actual_sprite

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return getattr(self._actual_sprite, name)

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        else:
            setattr(self._actual_sprite, name, value)

player_sprite_proxy = PlayerSpriteProxy()
