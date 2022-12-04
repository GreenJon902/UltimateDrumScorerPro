import math
from typing import Union

from betterLogger import ClassWithLogger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, OptionProperty, AliasProperty
from kivy.uix.widget import Widget

from committableButtonHandler import CommittableButtonHandler
from config.config import Config


class Bar(Widget, ClassWithLogger):
    transparency: int = NumericProperty()
    split_amount: int = NumericProperty()
    selection: Union[None, str] = OptionProperty(None, options=["left", "middle", "right"], allownone=True)

    def get_left_selected(self):
        return self.selection == "left"
    def set_left_selected(self, value):
        self.selection = "left" if value else None
    left_selected = AliasProperty(get_left_selected, set_left_selected, cache=True, bind=["selection"])

    def get_middle_selected(self):
        return self.selection == "middle"
    def set_middle_selected(self, value):
        self.selection = "middle" if value else None
    middle_selected = AliasProperty(get_middle_selected, set_middle_selected, cache=True, bind=["selection"])

    def get_right_selected(self):
        return self.selection == "right"
    def set_right_selected(self, value):
        self.selection = "right" if value else None
    right_selected = AliasProperty(get_right_selected, set_right_selected, cache=True, bind=["selection"])


    configurableness = NumericProperty()

    current_hover: Union[Color, None]

    def __init__(self, start_height=None, **kwargs):
        self.current_hover = None

        left_color = Color(rgb=(0, 0, 0))
        self.left_line = Line(width=Config.line_thickness)

        middle_color = Color(rgb=(0, 0, 0))
        self.middle_line = Line(width=Config.line_thickness)

        right_color = Color(rgb=(0, 0, 0))
        self.right_line = Line(width=Config.line_thickness)

        CommittableButtonHandler.register(self, left_color, self.check_left_collision, "transparency", "left_selected",
                                          "configurableness")
        CommittableButtonHandler.register(self, middle_color, self.check_middle_collision, "transparency",
                                          "middle_selected",
                                          "configurableness")
        CommittableButtonHandler.register(self, right_color, self.check_right_collision, "transparency",
                                          "right_selected", "configurableness")

        Widget.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.canvas.add(left_color)
        self.canvas.add(self.left_line)
        self.canvas.add(middle_color)
        self.canvas.add(self.middle_line)
        self.canvas.add(right_color)
        self.canvas.add(self.right_line)

        self.trigger_poses = Clock.create_trigger(self._do_poses, -1)
        self.fbind("pos", self.trigger_poses)
        self.fbind("size", self.trigger_poses)
        self.fbind("split_amount", self.trigger_poses)

        self.size_hint = None, None
        if start_height is None:
            self.height = Config.bar_spacing
        else:
            self.height = 0
            a = Animation(height=Config.bar_spacing, duration=Config.bar_entrance_speed)
            a.start(self)


        self.trigger_poses()

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

    def check_left_collision(self, pos):
        a = self.x
        b1 = self.x + Config.bar_side_width - self.split_amount

        ret = False
        if self.y - Config.bar_spacing / 2 < pos[1] < self.y + Config.bar_spacing / 2:
            if a < pos[0] < b1:
                ret = True
        return ret, math.fabs(pos[1] - self.y)

    def check_middle_collision(self, pos):
        b2 = self.x + (Config.bar_side_width + self.split_amount) * self.configurableness
        c1 = self.right - (Config.bar_side_width + self.split_amount) * self.configurableness

        ret = False
        if self.y - Config.bar_spacing / 2 < pos[1] < self.y + Config.bar_spacing / 2:
            if b2 < pos[0] < c1:
                ret = True
        return ret, math.fabs(pos[1] - self.y)

    def check_right_collision(self, pos):
        c2 = self.right - Config.bar_side_width + self.split_amount
        d = self.right

        ret = False
        if self.y - Config.bar_spacing / 2 < pos[1] < self.y + Config.bar_spacing / 2:
            if c2 < pos[0] < d:
                ret = True
        return ret, math.fabs(pos[1] - self.y)

