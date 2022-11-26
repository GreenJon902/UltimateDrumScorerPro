from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Line, Color
from kivy.uix.widget import Widget

from config.config import Config
from section import Section


class NoteStem(Line):
    def __init__(self, note, color, **kwargs):
        self.note = note
        self.color = color

        Line.__init__(self, **kwargs)
        self.width = Config.line_thickness
        note.fbind("x", self.update_pos)
        note.fbind("stem_x", self.update_pos)
        note.fbind("stem_bottom", self.update_pos)
        note.fbind("parent_multiplier", self.do_color)

        self.update_pos()

    def update_pos(self, *_):
        x = self.note.x + self.note.stem_x
        self.points = x, self.note.y + self.note.stem_bottom, x, self.note.top

    def do_color(self, *_):
        self.color.a = self.note.parent_multiplier

class Beat(Widget):
    stems: list[Line]

    def __init__(self, **kwargs):
        self.stems = list()

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
            self.add_new()


    def check_focus(self, *_):
        pos = Window.mouse_pos
        for child in self.children:
            if ((child.x - Config.section_x_buffer) <= pos[0] <= (child.right + Config.section_x_buffer) and
                    child.y <= pos[1] <= child.top):
                child.focused = True
            else:
                child.focused = False

    def add_widget(self, widget, index=0, **kwargs):
        fbind = widget.fbind
        fbind("size", self.trigger_layout)
        fbind("parent_x_buffer_multiplier", self.trigger_layout)
        Widget.add_widget(self, widget, index=index, **kwargs)

        with self.canvas:
            color = Color(rgb=(0, 0, 0), a=0)
            self.stems.insert(index, NoteStem(widget, color))

    def remove_widget(self, widget):
        funbind = widget.funbind
        funbind("size", self.trigger_layout)
        funbind("parent_x_buffer_multiplier", self.trigger_layout)
        Widget.remove_widget(self, widget)

    def do_layout(self, *_):
        x = self.x
        max_height = 0
        for child in self.children:
            x += Config.section_x_buffer * child.parent_multiplier

            child.x = x
            child.y = self.y

            x += child.width + Config.section_x_buffer * child.parent_multiplier

            if child.height > max_height:
                max_height = child.top

        self.width = x
        self.height = max_height - self.y

    def add_new(self, after=None):
        # New section needs to have committed notes or else it will kill itself for being empty, so either default hh
        # or copy last if possible
        if after is None:
            committed_notes = [1]
            index = 0
        else:
            committed_notes = after.committed_notes.copy()
            index = self.children.index(after) + 1
        self.add_widget(Section(entrance_animated=True, committed_notes=committed_notes), index=index)
