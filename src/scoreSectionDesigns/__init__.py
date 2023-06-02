from kivy.event import EventDispatcher
from kivy.graphics import *
from kivy.properties import ColorProperty

from kv import check_kv
from scoreSectionDesigns.fileHandling import read_design_from

check_kv()

from kv.settings import st


class Design(EventDispatcher):
    color = ColorProperty(defaultvalue=(0, 0, 0, 1))
    instructions: str

    def __init__(self, instructions, **kwargs):
        self.instructions = instructions
        EventDispatcher.__init__(self, **kwargs)

    def draw(self, color=True):
        if color:
            color = Color(rgba=self.color)
            self.bind(color=lambda _, value: setattr(color, "rgba", value))
        for instruction in self.instructions:
            instruction = instruction.replace("{st}", str(st))
            exec(instruction)

    def make_canvas(self, color=True):
        canvas = Canvas()
        with canvas:
            self.draw(color)
        return canvas

    def __call__(self, **kwargs):  # Create a new copy of this design with some settings
        kwa = {key: value.get(self) for key, value in self.properties().items()}
        kwa.update(kwargs)
        new = type(self)(self.instructions, **kwa)
        return new


__all__ = ["read_design_from", "Design"]
