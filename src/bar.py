from kivy.clock import Clock
from kivy.graphics import Line, Color
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget

from config.config import Config


class Bars(Widget):
    bar_number: int = NumericProperty()
    lines: list[Line]

    def __init__(self, section, **kwargs):
        self.section = section

        self.lines = list()
        self.trigger_posses = Clock.create_trigger(self._do_posses, -1)

        Widget.__init__(self, **kwargs)
        self.fbind("pos", self.trigger_posses)
        self.fbind("size", self.trigger_posses)
        self.section.fbind("parent_multiplier", self.do_transparency)

        with self.canvas:
            self.color = Color(rgb=(0, 0, 0), a=0)

        self.on_bar_number(self, self.bar_number)
        self.do_transparency()

    def on_bar_number(self, _, value):
        self.height = (value - 1) * Config.bar_spacing

        for line in self.lines:
            self.canvas.remove(line)
        self.lines.clear()
        with self.canvas:
            for i in range(value):
                self.lines.append(Line(width=Config.line_thickness))

        self.trigger_posses()

    def _do_posses(self, *_):
        y = self.y

        for line in self.lines:
            line.points = self.x, y, self.right, y
            y += Config.bar_spacing

    def do_transparency(self, *_):
        self.color.a = self.section.parent_multiplier
