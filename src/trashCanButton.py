from typing import Callable

from betterLogger import ClassWithLogger
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout

from config.config import Config


class TrashCanButton(RelativeLayout, ClassWithLogger):
    transparency: int = NumericProperty()

    def __init__(self, size, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.size = size
        self.size_hint = None, None

        with self.canvas:
            self.color = Color(rgb=(1, 0, 0), a=self.transparency)

            Line(points=(0.1 * size[0], 0.8 * size[1],
                         0.2 * size[0], 0,
                         0.8 * size[0], 0,
                         0.9 * size[0], 0.8 * size[1],

                         1 * size[0], 0.8 * size[1],
                         1 * size[0], 0.9 * size[1],
                         0.6 * size[0], 0.9 * size[1],
                         0.6 * size[0], 1 * size[1],
                         0.4 * size[0], 1 * size[1],
                         0.4 * size[0], 0.9 * size[1],
                         0.6 * size[0], 0.9 * size[1],  # under handle
                         0 * size[0], 0.9 * size[1],
                         0 * size[0], 0.8 * size[1],
                         1 * size[0], 0.8 * size[1]  # Close lid
                         ),
                 width=Config.line_thickness)


    def on_transparency(self, _, a):
        self.color.a = a
