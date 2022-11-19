import math

from betterLogger import ClassWithLogger
from kivy.graphics import Line, Color, Triangle
from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout

from config.config import Config


class Symbol(RelativeLayout, ClassWithLogger):
    transparency: int = NumericProperty(defaultvalue=1)

    def __init__(self, name, size, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.size = size
        self.size_hint = None, None

        with self.canvas:
            self.color = Color(rgb=(0, 0, 0), a=self.transparency)

            if name == "tilted_line":
                Line(points=(0, -size[1]/2, size[0], 0), width=Config.line_thickness)

            elif name == "tilted_line_with_arc":
                Line(points=(0, -size[1]/2, size[0], 0), width=Config.line_thickness)
                Line(ellipse=(Config.line_thickness, Config.line_thickness,
                              -size[0] * 1/4, -size[1] * 1/4,
                              30, 270), width=Config.line_thickness)

            elif name == "oval_with_tilted_line":
                Line(ellipse=(0, -size[1]/2, size[0], size[1]), width=Config.line_thickness)

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

                Line(points=(-x1, y1, -x2, y2), width=Config.line_thickness) # Minus x because the equation was made
                                                                             # when (0,0) was on the right

            elif name == "cross":
                Line(points=(size[0], 0, 0, -size[1]/2), width=Config.line_thickness)
                Line(points=(size[0], -size[1]/2, 0, 0), width=Config.line_thickness)

            elif name == "circled_cross":
                Line(ellipse=(0, -size[1] / 2, size[0], size[1]), width=Config.line_thickness)

                a = size[1]
                b = size[0]
                x1 = (-math.sqrt(a ** 2 * b ** 2 * (a ** 2 + b ** 2)) - a ** 2 * b - b ** 3) / (2 * (a ** 2 + b ** 2))
                y1 = (-math.sqrt(a ** 2 * b ** 2 * (a ** 2 + b ** 2))) / (2 * (a ** 2 + b ** 2))

                x2 = (math.sqrt(a ** 2 * b ** 2 * (a ** 2 + b ** 2)) - a ** 2 * b - b ** 3) / (2 * (a ** 2 + b ** 2))
                y2 = (math.sqrt(a ** 2 * b ** 2 * (a ** 2 + b ** 2))) / (2 * (a ** 2 + b ** 2))

                Line(points=(-x1, y1, -x2, y2), width=Config.line_thickness)
                Line(points=(-x1, y2, -x2, y1), width=Config.line_thickness)

            elif name == "8_cross":
                Line(points=(0, 0, size[0], 0), width=Config.line_thickness)
                Line(points=(size[0]/2, -size[1]/2, size[0]/2, size[1]/2), width=Config.line_thickness)

                Line(points=(0, size[1]/2, size[0], -size[1]/2), width=Config.line_thickness)
                Line(points=(0, -size[1]/2, size[0], size[1]/2), width=Config.line_thickness)

            elif name == "rotated_square":
                Line(points=(0, 0,
                             size[0] / 2, -size[1] / 2,
                             size[0], 0,
                             size[0] / 2, size[1] / 2), close=True, joint="miter", width=Config.line_thickness)

                Triangle(points=[0, 0,
                                 size[0]/2, -size[1]/2,
                                 size[0], 0])
                Triangle(points=[0, 0,
                                 size[0] / 2, size[1] / 2,
                                 size[0], 0])

            elif name == "hollow_rotated_square":
                Line(points=(0, 0,
                             size[0]/2, -size[1]/2,
                             size[0], 0,
                             size[0]/2, size[1]/2), close=True, joint="miter", width=Config.line_thickness)

            else:
                self.log_error(f"No symbol called \"{name}\"")

    def get_absolute_center(self):
        return self.to_window(self.width/2, 0, initial=False)


    def on_transparency(self, _, a):
        self.color.a = a
