from typing import Union

from betterLogger import ClassWithLogger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, OptionProperty
from kivy.uix.widget import Widget

from config.config import Config


class Bar(Widget, ClassWithLogger):
    transparency: int = NumericProperty()
    split_amount: int = NumericProperty()
    selection: Union[None, str] = OptionProperty("middle", options=["left", "middle", "right"], allownone=True)
    configurableness = NumericProperty()

    current_hover: Union[Color, None]

    def __init__(self, start_height=None, **kwargs):
        self.current_hover = None

        Widget.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.trigger_poses = Clock.create_trigger(self._do_poses, -1)
        self.fbind("pos", self.trigger_poses)
        self.fbind("size", self.trigger_poses)
        self.fbind("split_amount", self.trigger_poses)
        self.fbind("transparency", self.do_transparency)
        self.fbind("selection", self.do_transparency)
        self.fbind("configurableness", self.do_transparency)
        self.fbind("pos", lambda _, pos: self.mouse_move(Window.mouse_pos))
        Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

        self.size_hint = None, None
        if start_height is None:
            self.height = Config.bar_spacing
        else:
            self.height = 0
            a = Animation(height=Config.bar_spacing, duration=Config.bar_entrance_speed)
            a.start(self)

        with self.canvas:
            self.left_color = Color(rgb=(0, 0, 0))
            self.left_line = Line(width=Config.line_thickness)

            self.middle_color = Color(rgb=(0, 0, 0))
            self.middle_line = Line(width=Config.line_thickness)

            self.right_color = Color(rgb=(0, 0, 0))
            self.right_line = Line(width=Config.line_thickness)

        self.trigger_poses()
        self.do_transparency()

    def _do_poses(self, *_):
        a = self.x
        b1 = self.x + Config.bar_side_width - self.split_amount
        b2 = self.x + (Config.bar_side_width + self.split_amount) * self.configurableness
        c1 = self.right - (Config.bar_side_width + self.split_amount) * self.configurableness
        c2 = self.right - Config.bar_side_width + self.split_amount
        d = self.right

        self.left_line.points = a, self.y, b1, self.y
        self.middle_line.points = b2, self.y, c1, self.y
        self.right_line.points = c2, self.y, d, self.y

    def do_transparency(self, *_):
        self.left_color.a = self.transparency * (1 if self.selection == "left" else
                                                 Config.bar_selector_uncommitted_transparency * self.configurableness)
        self.middle_color.a = self.transparency * (1 if self.selection == "middle" else
                                                   Config.bar_selector_uncommitted_transparency * self.configurableness)
        self.right_color.a = self.transparency * (1 if self.selection == "right" else
                                                  Config.bar_selector_uncommitted_transparency * self.configurableness)

    def mouse_move(self, pos):
        a = self.x
        b1 = self.x + Config.bar_side_width - self.split_amount
        b2 = self.x + (Config.bar_side_width + self.split_amount) * self.configurableness
        c1 = self.right - (Config.bar_side_width + self.split_amount) * self.configurableness
        c2 = self.right - Config.bar_side_width + self.split_amount
        d = self.right

        new_hover = None
        name = None
        if self.y - Config.bar_spacing / 2 < pos[1] < self.y + Config.bar_spacing / 2:
            if a < pos[0] < b1:
                new_hover = self.left_color
                name = "left"
            elif b2 < pos[0] < c1:
                new_hover = self.middle_color
                name = "middle"
            elif c2 < pos[0] < d:
                new_hover = self.right_color
                name = "right"

        if self.current_hover != new_hover:
            if self.current_hover is not None:
                a = Animation(r=0, b=0, g=0, duration=Config.bar_selector_hover_fade_speed)
                a.start(self.current_hover)
                self.current_hover = None

            if new_hover is not None:
                a = Animation(r=(Config.bar_selector_committed_hover_color[0] if self.selection == name else
                                 Config.bar_selector_uncommitted_hover_color[0]),
                              b=(Config.bar_selector_committed_hover_color[1] if self.selection == name else
                                 Config.bar_selector_uncommitted_hover_color[1]),
                              g=(Config.bar_selector_committed_hover_color[2] if self.selection == name else
                                 Config.bar_selector_uncommitted_hover_color[2]),
                              duration=Config.bar_selector_hover_fade_speed)
                a.start(new_hover)
                self.current_hover = new_hover

    def on_touch_up(self, touch):
        pos = touch.pos

        a = self.x
        b1 = self.x + Config.bar_side_width - self.split_amount
        b2 = self.x + (Config.bar_side_width + self.split_amount) * self.configurableness
        c1 = self.right - (Config.bar_side_width + self.split_amount) * self.configurableness
        c2 = self.right - Config.bar_side_width + self.split_amount
        d = self.right

        name = None
        did_click = False
        new_hover = None
        if self.y - Config.bar_spacing / 2 < pos[1] < self.y + Config.bar_spacing / 2:
            if a < pos[0] < b1:
                name = "left"
                did_click = True
                new_hover = self.left_color
            elif b2 < pos[0] < c1:
                name = "middle"
                did_click = True
                new_hover = self.middle_color
            elif c2 < pos[0] < d:
                name = "right"
                did_click = True
                new_hover = self.right_color

        if did_click:
            if name == self.selection:
                self.selection = None
            else:
                self.selection = name

            a = Animation(r=(Config.bar_selector_committed_hover_color[0] if self.selection == name else
                             Config.bar_selector_uncommitted_hover_color[0]),
                          b=(Config.bar_selector_committed_hover_color[1] if self.selection == name else
                             Config.bar_selector_uncommitted_hover_color[1]),
                          g=(Config.bar_selector_committed_hover_color[2] if self.selection == name else
                             Config.bar_selector_uncommitted_hover_color[2]),
                          duration=Config.bar_selector_hover_fade_speed)
            a.start(new_hover)
