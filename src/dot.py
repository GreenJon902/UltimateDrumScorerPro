import math

from betterLogger import ClassWithLogger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.widget import Widget

from committableButtonHandler import CommittableButtonHandler
from config.config import Config


class Dot(Widget, ClassWithLogger):
    transparency: int = NumericProperty()
    committed: bool = BooleanProperty()

    configurableness: int = NumericProperty()

    def __init__(self, start_width=None, **kwargs):
        color = Color(rgb=(0, 0, 0))
        self.dot = Line(width=Config.line_thickness)

        CommittableButtonHandler.register(self, color, self.check_collision, "transparency", "committed",
                                          "configurableness")

        Widget.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)
        self.canvas.add(color)
        self.canvas.add(self.dot)

        self.trigger_poses = Clock.create_trigger(self._do_poses, -1)
        self.fbind("pos", self.trigger_poses)


        if start_width is None:
            self.width = Config.dot_x_spacing
        else:
            self.width = 0
            a = Animation(width=Config.dot_x_spacing, duration=Config.dot_entrance_speed)
            a.start(self)

    def _do_poses(self, *_):
        self.dot.circle = (*self.pos, Config.dot_radius)

    def check_collision(self, pos):
        distance = math.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)
        return distance <= Config.dot_selector_hover_radius, distance
