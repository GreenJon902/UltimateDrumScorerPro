from kivy.graphics import *
from kivy.properties import ColorProperty
from kivy.uix.widget import Widget

from kv import check_kv
from scoreSectionDesigns.fileHandling import read_design_from

check_kv()

from kv.settings import st


class Design(Widget):
    color = ColorProperty(defaultvalue=(0, 0, 0, 1))
    instructions: str

    def __init__(self, instructions, **kwargs):
        self.instructions = instructions
        Widget.__init__(self, **kwargs)

    def draw(self):
        color = Color(rgba=self.color)
        self.bind(color=lambda _, value: setattr(color, "rgba", value))
        for instruction in self.instructions:
            instruction = instruction.replace("'{st}'", str(st))
            exec(instruction)

    def make_canvas(self):
        canvas = Canvas()
        with canvas:
            self.draw()
        return canvas


__all__ = ["read_design_from", "Design"]
