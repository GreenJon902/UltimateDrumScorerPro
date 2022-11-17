from kivy import metrics
from kivy.graphics import Line, PushMatrix, Scale, PopMatrix
from kivy.properties import StringProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from config.config import Config


class Symbol(RelativeLayout):
    def __init__(self, name, size, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        with self.canvas:
            PushMatrix()

            if name == "tilted_line":
                Line(points=(0, 0, -size[0], -size[1]), width=Config.line_thickness)

            PopMatrix()
