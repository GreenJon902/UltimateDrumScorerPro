from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.uix.widget import Widget

from config.config import Config


class Stem(Widget):
    def __init__(self, section, **kwargs):
        self.section = section

        Widget.__init__(self, **kwargs)

        self.trigger_posses = Clock.create_trigger(self._do_posses, -1)
        self.fbind("pos", self.trigger_posses)
        self.fbind("size", self.trigger_posses)
        self.section.fbind("parent_multiplier", self.do_transparency)

        with self.canvas:
            self.color = Color(rgb=(0, 0, 0), a=0)
            self.line = Line(width=Config.line_thickness)

        self.do_transparency()

    def _do_posses(self, *_):
        self.line.points = self.x, self.y, self.x, self.top

    def do_transparency(self, *_):
        self.color.a = self.section.parent_multiplier
