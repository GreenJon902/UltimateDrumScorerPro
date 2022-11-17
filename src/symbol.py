import math

from betterLogger import ClassWithLogger
from kivy import metrics
from kivy.graphics import Line, PushMatrix, Scale, PopMatrix, Ellipse, Rotate
from kivy.properties import StringProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from config.config import Config


class Symbol(RelativeLayout, ClassWithLogger):
    def __init__(self, name, size, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        with self.canvas:
            if name == "tilted_line":
                Line(points=(0, 0, -size[0], -size[1]), width=Config.line_thickness)

            elif name == "oval_with_tilted_line":
                Line(ellipse=(-size[0], -size[1]/2, size[0], size[1]), width=Config.line_thickness)

                # Get the coordinates of where the points of the line y=0.5x+b/4 intersect with an ellipse with the size
                # b by a
                #
                # ellipse equation is ((y ^ 2) / ((a / 2) ^ 2)) + (((x + (b / 2)) ^ 2) / ((b / 2) ^ 2)) = 1

                a = size[1]
                b = size[0]
                x1 = (-2 * math.sqrt(a ** 2 * b ** 2 * (4 * a ** 2 + b ** 2)) - 4 * a ** 2 * b - b ** 3) / (
                            2 * (4 * a ** 2 + b ** 2))
                y1 = -math.sqrt(a ** 2 * b ** 2 * (4 * a ** 2 + b ** 2)) / (2 * (4 * a ** 2 + b ** 2))

                x2 = (2 * math.sqrt(a ** 2 * b ** 2 * (4 * a ** 2 + b ** 2)) - 4 * a ** 2 * b - b ** 3) / (
                            2 * (4 * a ** 2 + b ** 2))
                y2 = math.sqrt(a ** 2 * b ** 2 * (4 * a ** 2 + b ** 2)) / (2 * (4 * a ** 2 + b ** 2))

                Line(points=(x1, y1, x2, y2), width=Config.line_thickness)

            else:
                self.log_error(f"No symbol called \"{name}\"")
