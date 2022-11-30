import math

from betterLogger import ClassWithLogger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.widget import Widget

from config.config import Config


class Dot(Widget, ClassWithLogger):
    transparency: int = NumericProperty()
    configurableness: int = NumericProperty()
    committed: bool = BooleanProperty()
    hovered = False

    def __init__(self, start_width=None, **kwargs):
        self.current_hover = None

        Widget.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.trigger_poses = Clock.create_trigger(self._do_poses, -1)
        self.fbind("pos", self.trigger_poses)
        self.fbind("configurableness", self.do_transparency)#
        self.fbind("transparency", self.do_transparency)
        self.fbind("committed", self.do_transparency)
        Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

        if start_width is None:
            self.width = Config.dot_x_spacing
        else:
            self.width = 0
            a = Animation(width=Config.dot_x_spacing, duration=Config.dot_entrance_speed)
            a.start(self)

        with self.canvas:
            self.color = Color(rgb=(0, 0, 0))
            self.dot = Line(width=Config.line_thickness)

        self.do_transparency()

    def _do_poses(self, *_):
        self.dot.circle = (*self.pos, Config.dot_radius)

    def do_transparency(self, *_):
        self.color.a = (1 if self.committed else
                        (Config.dot_selector_uncommitted_transparency * self.configurableness)) * self.transparency

    def mouse_move(self, pos):
        distance = math.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)
        if distance <= Config.dot_selector_hover_radius:
            if not self.hovered:
                a = Animation(r=(Config.dot_selector_committed_hover_color[0] if self.committed else
                                 Config.dot_selector_uncommitted_hover_color[0]),
                              b=(Config.dot_selector_committed_hover_color[1] if self.committed else
                                 Config.dot_selector_uncommitted_hover_color[1]),
                              g=(Config.dot_selector_committed_hover_color[2] if self.committed else
                                 Config.dot_selector_uncommitted_hover_color[2]),
                              duration=Config.dot_selector_hover_fade_speed)
                a.start(self.color)
                self.hovered = True
        elif self.hovered:
            a = Animation(r=0,
                          b=0,
                          g=0,
                          duration=Config.dot_selector_hover_fade_speed)
            a.start(self.color)
            self.hovered = False

    def on_touch_up(self, touch):
        pos = touch.pos
        distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        if distance <= Config.dot_selector_hover_radius:
            if self.committed:
                self.committed = False
            else:
                self.committed = True

            a = Animation(r=(Config.dot_selector_committed_hover_color[0] if self.committed else
                             Config.dot_selector_uncommitted_hover_color[0]),
                          b=(Config.dot_selector_committed_hover_color[1] if self.committed else
                             Config.dot_selector_uncommitted_hover_color[1]),
                          g=(Config.dot_selector_committed_hover_color[2] if self.committed else
                             Config.dot_selector_uncommitted_hover_color[2]),
                          duration=Config.dot_selector_hover_fade_speed)
            a.start(self.color)