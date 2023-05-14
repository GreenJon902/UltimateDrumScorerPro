from typing import Union

from kivy.core.text import Label as CoreLabel
from kivy.core.text.markup import MarkupLabel as CoreMarkupLabel
from kivy.graphics import *

from renderer.text.text_rendererBase import Text_RendererBase


class Text_NormalRenderer(Text_RendererBase):
    label: Union[CoreLabel, CoreMarkupLabel] = None  # Cache the label
    label_do_formatting: bool = None
    rect: Rectangle  # Draws our texture to the canvas

    def __init__(self):
        Text_RendererBase.__init__(self)

        with self.canvas:
            self.rect = Rectangle()

    def update(self, text, do_formatting, font_size):
        self.choose_label(do_formatting)
        self.update_label_options(text, font_size)
        self.render_label()

    def choose_label(self, do_formatting):
        if self.label is None or self.label_do_formatting != do_formatting:
            if do_formatting:
                self.label = CoreMarkupLabel()
            else:
                self.label = CoreLabel()
            self.label_do_formatting = do_formatting

    def update_label_options(self, text, font_size):
        self.label.text = text
        self.label.options["font_size"] = font_size

    def render_label(self):
        self.label.refresh()
        self.label.texture.bind()
        self.size = self.get_label_size()

        self.rect.size = self.size
        self.rect.texture = self.label.texture

    def get_label_size(self):
        return self.label.texture.size


__all__ = ["Text_NormalRenderer"]
