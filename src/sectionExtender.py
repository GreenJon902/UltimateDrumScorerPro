from betterLogger import ClassWithLogger
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout

from config.config import Config


class SectionExtender(RelativeLayout, ClassWithLogger):
    transparency: int = NumericProperty()

    def __init__(self, height, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.size_hint = None, None
        self.height = height

        with self.canvas:
            self.color = Color(rgb=(0, 0, 0), a=self.transparency)

            self.line = Line(width=Config.line_thickness)
        self.repoint()
        self.bind(size=lambda _, __: self.repoint())

    def repoint(self):
        arrow_edge_x = (self.size[0] - self.size[1]/2)
        if arrow_edge_x < 0:
            arrow_edge_x = 0

        self.line.points = (0, 0,
                            0, self.size[1],
                            0, 0.5 * self.size[1],
                            1 * self.size[0], 0.5 * self.size[1],
                            arrow_edge_x, 0,
                            1 * self.size[0], 0.5 * self.size[1],
                            arrow_edge_x, self.size[1])


    def on_transparency(self, _, a):
        self.color.a = a

    def over_arrow(self, x, y):
        arrow_edge_x = (self.size[0] - self.size[1] / 2)
        if arrow_edge_x < 0:
            arrow_edge_x = 0

        return self.collide_point(x, y) and x > arrow_edge_x
