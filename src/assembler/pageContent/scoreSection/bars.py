import typing

from kivy.clock import Clock
from kivy.graphics import Instruction, Line, Color, InstructionGroup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from score.notes import bar_height, bar_width

if typing.TYPE_CHECKING:
    from assembler.pageContent.scoreSection import MultiNoteHolder


class MultiBarHolder(Widget):
    note_container: "MultiNoteHolder"

    def __init__(self, note_container, **kwargs):
        self.trigger_sizing = Clock.create_trigger(self.do_sizing, -1)
        self.trigger_layout = Clock.create_trigger(self.do_layout, -1)
        self.note_container = note_container
        note_container.bind(size=self.trigger_sizing)

        Widget.__init__(self, **kwargs)
        self.fbind("children", self.trigger_sizing)
        self.fbind("children", self.trigger_layout)
        self.fbind("pos", self.trigger_layout)
        self.fbind("size", self.trigger_layout)

        self.trigger_sizing()  # Which then causes layout

    def add_widget(self, widget, **kwargs):
        widget.fbind("height", self.trigger_sizing)
        Widget.add_widget(self, widget, **kwargs)

    def remove_widget(self, widget):
        widget.funbind("height", self.trigger_sizing)
        Widget.remove_widget(self, widget)

    def do_sizing(self, *_):
        self.width = self.note_container.width
        self.height = sum(child.height for child in self.children)

    def do_layout(self, *_):
        y = self.y
        for child in self.children:
            child.x = self.x
            child.width = self.width
            child.y = y
            y += child.height


class Bar(Widget):
    def __init__(self, **kwargs):
        Widget.__init__(self, height=bar_height, **kwargs)


def update_line_points(line: Line, start: Widget, end: Widget):
    line.points = start.right, start.y, end.right, end.y
    line.flag_update()


def draw_bar(start: Widget, end: Widget) -> Instruction:
    ret = InstructionGroup()
    ret.add(Color(rgba=(0, 0, 0, 1)))
    line = Line(points=[start.right, start.y, end.right, end.y], width=bar_width)
    start.bind(pos=lambda _, _2: update_line_points(line, start, end))
    end.bind(pos=lambda _, _2: update_line_points(line, start, end))
    ret.add(line)
    return ret
