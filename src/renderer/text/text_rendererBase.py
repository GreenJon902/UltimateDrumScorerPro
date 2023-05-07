from kivy.core.image import Texture
from kivy.graphics import Canvas


class Text_RendererBase:
    size: tuple[float, float]
    canvas: Canvas
    texture: Texture

    def __init__(self):
        self.canvas = Canvas()

    def update(self, text, do_formatting, font_size):
        raise NotImplementedError()


__all__ = ["Text_RendererBase"]
