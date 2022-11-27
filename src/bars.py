from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.widget import Widget

from bar import Bar
from config.config import Config


class Bars(Widget):
    focused: bool = BooleanProperty(defaultvalue=False)
    focused_amount: bool = NumericProperty()  # Triggered by focused

    bars: list[Bar]
    split = False

    def __init__(self, bar_number, **kwargs):
        self.bars = list()
        self.trigger_posses = Clock.create_trigger(self._do_posses, -1)

        Widget.__init__(self, **kwargs)
        self.fbind("pos", self.trigger_posses)
        self.fbind("width", self.trigger_posses)
        self.fbind("focused_amount", self.trigger_posses)
        self.fbind("children", self.trigger_posses)
        Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

        for i in range(bar_number):
            bar = Bar()
            bar.transparency = 1
            self.add_widget(bar)
            self.bars.append(bar)

        self.new_bar_bar = Bar()  # For adding new bars
        self.new_bar_bar.transparency = 1
        self.new_bar_bar.selection = None
        self.add_widget(self.new_bar_bar)
        self.new_bar_bar.bind(selection=self.new_bar_bar_selected)

    def new_bar_bar_selected(self, new_bar_bar, _):
        self.bars.insert(0, new_bar_bar)
        new_bar_bar.unbind(selection=self.new_bar_bar_selected)

        self.new_bar_bar = Bar(start_height=0)  # For adding new bars
        self.new_bar_bar.transparency = 1
        self.new_bar_bar.selection = None
        self.new_bar_bar.configurableness = 1
        self.new_bar_bar.split_amount = Config.bar_split_amount
        self.add_widget(self.new_bar_bar)
        self.new_bar_bar.fbind("selection", self.new_bar_bar_selected)

        self.trigger_posses()

    def _do_posses(self, *_):
        for child in self.children:
            child.x = self.x
            child.width = self.width

        self.new_bar_bar.y = self.y + Config.bar_spacing

        y = self.y + (Config.bar_spacing + self.new_bar_bar.height) * self.focused_amount
        height = 0
        bar = None
        for bar in self.bars:
            bar.y = y
            y += bar.height
            height += bar.height
        if bar is not None:
            height -= bar.height

        self.height = height + (Config.bar_spacing + self.new_bar_bar.height) * self.focused_amount

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

    def remove_bar(self, bar):
        self.bars.remove(bar)
        self.remove_widget(bar)

    def on_focused_amount(self, _, focused_amount):
        for child in self.children:
            child.configurableness = focused_amount

    def mouse_move(self, pos):
        if self.collide_point(*pos):
            if not self.split:
                a = Animation(split_amount=Config.bar_split_amount, duration=Config.bar_split_speed)
                for child in self.children:
                    a.start(child)
                self.split = True
        elif self.split:
            a = Animation(split_amount=0, duration=Config.bar_split_speed)
            for child in self.children:
                a.start(child)
            self.split = False

    def add_widget(self, widget, index=0, canvas=None):
        Widget.add_widget(self, widget, index=index, canvas=canvas)
        widget.fbind("height", self.trigger_posses)
