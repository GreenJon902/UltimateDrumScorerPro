from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.widget import Widget

from bar import Bar
from config.config import Config
from dot import Dot
from section import Section


class Bars(Widget):
    dot_width: int = NumericProperty()  # For parent, the minimum width this can be because of dots

    focused: bool = BooleanProperty(defaultvalue=False)
    focused_amount: bool = NumericProperty()  # Triggered by focused

    bars: list[Bar]
    dots: list[Dot]
    split = False

    section: Section

    def __init__(self, section, bars, dot_number, **kwargs):
        self.section = section

        self.bars = list()
        self.dots = list()
        self.trigger_posses = Clock.create_trigger(self._do_posses, -1)

        Widget.__init__(self, **kwargs)
        self.fbind("pos", self.trigger_posses)
        self.fbind("width", self.trigger_posses)
        self.fbind("focused_amount", self.trigger_posses)
        self.fbind("children", self.trigger_posses)
        self.section.fbind("parent_multiplier", self.do_transparency)
        Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

        for i in range(len(bars)):
            bar = Bar()
            bar.transparency = 1
            bar.selection = bars[i]
            self.add_widget(bar)
            self.bars.append(bar)

        for i in range(dot_number):
            dot = Dot()
            dot.transparency = 1
            self.add_widget(dot)
            self.dots.append(dot)

        self.new_bar_bar = Bar()  # For adding new bars
        self.new_bar_bar.transparency = 1
        self.new_bar_bar.selection = None
        self.add_widget(self.new_bar_bar)
        self.new_bar_bar.bind(selection=self.new_bar_bar_selected)

        self.new_dot_dot = Dot()  # For adding new dots
        self.new_dot_dot.transparency = 1
        self.new_dot_dot.committed = False
        self.add_widget(self.new_dot_dot)
        self.new_dot_dot.bind(committed=self.new_dot_dot_committed)

    def do_transparency(self, *_):
        for child in self.children:
            child.transparency = self.section.parent_multiplier

    def new_bar_bar_selected(self, new_bar_bar, _):
        self.bars.insert(0, new_bar_bar)
        new_bar_bar.unbind(selection=self.new_bar_bar_selected)

        self.new_bar_bar = Bar(start_height=0)  # For adding new bars
        self.new_bar_bar.transparency = 1
        self.new_bar_bar.selection = None
        self.new_bar_bar.configurableness = 1
        self.new_bar_bar.split_amount = Config.bar_split_amount
        self.add_widget(self.new_bar_bar)
        self.new_bar_bar.bind(selection=self.new_bar_bar_selected)

        self.trigger_posses()

    def new_dot_dot_committed(self, new_dot_dot, _):
        self.dots.insert(0, new_dot_dot)
        new_dot_dot.unbind(committed=self.new_dot_dot_committed)

        self.new_dot_dot = Dot(start_width=0)  # For adding new dots
        self.new_dot_dot.transparency = 1
        self.new_dot_dot.committed = False
        self.new_dot_dot.configurableness = 1
        self.add_widget(self.new_dot_dot)
        self.new_dot_dot.bind(committed=self.new_dot_dot_committed)

        self.trigger_posses()

    def _do_posses(self, *_):
        for child in self.children:
            if isinstance(child, Bar):
                child.x = self.x
                child.width = self.width
            else:  # Dot
                child.y = self.y


        dot_x = self.x + Config.dot_x_buffer
        self.new_dot_dot.x = dot_x
        dot_x += self.new_dot_dot.width * self.focused_amount
        for dot in self.dots:
            dot.x = dot_x
            dot_x += dot.width
        self.dot_width = dot_x - self.x


        self.new_bar_bar.y = self.y + Config.bar_dot_height

        y = self.y + Config.bar_dot_height + self.new_bar_bar.height * self.focused_amount
        height = 0
        bar = None
        for bar in self.bars:
            bar.y = y
            y += bar.height
            height += bar.height
        if bar is not None:
            height -= bar.height  # Last one
        else:
            height -= self.new_bar_bar.height * self.focused_amount

        self.height = height + Config.bar_dot_height + self.new_bar_bar.height * self.focused_amount

    def on_focused(self, _, focused):
        if focused:
            a = Animation(focused_amount=1, duration=Config.focus_speed)
            a.start(self)
        else:
            a = Animation(focused_amount=0, duration=Config.focus_speed)
            a.start(self)

            for bar in self.bars:
                if bar.selection is None:
                    a = Animation(height=0, transparency=0, duration=Config.bar_kill_speed)
                    a.start(bar)
                    Clock.schedule_once(lambda _, bar_=bar: self.remove_bar(bar_), Config.bar_kill_speed)

            for dot in self.dots:
                if not dot.committed:
                    a = Animation(width=0, transparency=0, duration=Config.dot_kill_speed)
                    a.start(dot)
                    Clock.schedule_once(lambda _, dot_=dot: self.remove_dot(dot_), Config.dot_kill_speed)

    def remove_bar(self, bar):
        self.bars.remove(bar)
        self.remove_widget(bar)

    def remove_dot(self, dot):
        self.dots.remove(dot)
        self.remove_widget(dot)

    def on_focused_amount(self, _, focused_amount):
        for child in self.children:
            child.configurableness = focused_amount

    def mouse_move(self, pos):
        if self.collide_point(*pos):
            if not self.split:
                a = Animation(split_amount=Config.bar_split_amount, duration=Config.bar_split_speed)
                for child in self.children:
                    if isinstance(child, Bar):
                        a.start(child)
                self.split = True
        elif self.split:
            a = Animation(split_amount=0, duration=Config.bar_split_speed)
            for child in self.children:
                if isinstance(child, Bar):
                    a.start(child)
            self.split = False

    def add_widget(self, widget, index=0, canvas=None):
        Widget.add_widget(self, widget, index=index, canvas=canvas)
        widget.fbind("height", self.trigger_posses)
        widget.fbind("width", self.trigger_posses)

    def get_bars(self):
        bars = list()
        for bar in self.bars:
            if bar.selection is not None:
                bars.append(bar.selection)
        return bars

    def get_dot_number(self):
        n = 0
        for dot in self.dots:
            if dot.committed:
                n += 1
        return n
