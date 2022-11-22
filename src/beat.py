from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Translate, PushMatrix, PopMatrix
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from config.config import Config
from section import Section


class Beat(Widget):
    def __init__(self, **kwargs):
        self.trigger_layout = Clock.create_trigger(self.do_layout, -1)
        self.trigger_focus_check = Clock.create_trigger(self.check_focus, -1)

        Window.bind(mouse_pos=self.trigger_focus_check)
        fbind = self.fbind
        fbind('pos', self.trigger_layout)
        fbind('children', self.trigger_layout)
        fbind('pos', self.trigger_focus_check)
        fbind('width', self.trigger_focus_check)

        Widget.__init__(self, **kwargs)

        for i in range(Config.default_beat_section_count):
            self.add_widget(Section(committed_notes=[1]))


    def check_focus(self, *_):
        pos = Window.mouse_pos
        for child in self.children:
            if ((child.x - Config.section_x_buffer) <= pos[0] <= (child.right + Config.section_x_buffer) and
                    child.y <= pos[1] <= child.top):
                child.focused = True
            else:
                child.focused = False

    def add_widget(self, widget, *args, **kwargs):
        fbind = widget.fbind
        fbind("size", self.trigger_layout)
        Widget.add_widget(self, widget, *args, **kwargs)

    def remove_widget(self, widget):
        funbind = widget.funbind
        funbind("size", self.trigger_layout)
        Widget.remove_widget(self, widget)

    def do_layout(self, *_):
        x = self.x
        max_height = 0
        for child in self.children:
            x += Config.section_x_buffer

            child.x = x
            child.y = self.y

            x += child.width + Config.section_x_buffer

            if child.height > max_height:
                max_height = child.top

        self.width = x
        self.height = max_height - self.y
