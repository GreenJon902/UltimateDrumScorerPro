from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.graphics import *
from kivy.properties import ColorProperty

from kv import check_kv
from scoreSectionDesigns.fileHandling import read_design_from

check_kv()

from kv.settings import st


def format_value(v, **kwargs):
    if type(v) == str:
        kwargs.setdefault("st", str(st))
        v = v.format(**kwargs)

        if v[0:4] == "eval":
            v = eval(v[4:])
    return v


class Design(EventDispatcher):
    color = ColorProperty(defaultvalue=(0, 0, 0, 1))
    instructions: tuple[str, dict[str, any]]

    def __init__(self, instructions, **kwargs):
        self.instructions = instructions
        EventDispatcher.__init__(self, **kwargs)

    def draw(self, color=True, **kwargs):
        if color:
            color = Color(rgba=self.color)
            self.bind(color=lambda _, value: setattr(color, "rgba", value))
        for instruction in self.instructions:
            attrs = {}
            for kw, v in instruction[1].items():
                v = format_value(v, **kwargs)
                attrs[kw] = v

            if instruction[0] == "Translate":  # Waiting on https://github.com/kivy/kivy/pull/8270
                x = attrs.pop("x", 0)
                y = attrs.pop("y", 0)
                z = attrs.pop("z", 0)
                Factory.get(instruction[0])(x, y, z, **attrs)
            elif instruction[0] == "Scale":  # Waiting on https://github.com/kivy/kivy/pull/8270
                x = attrs.pop("x", 1)
                y = attrs.pop("y", 1)
                z = attrs.pop("z", 1)
                Factory.get(instruction[0])(x, y, z, **attrs)
            else:
                Factory.get(instruction[0])(**attrs)

    def make_canvas(self, color=True, **kwargs):
        canvas = Canvas()
        with canvas:
            self.draw(color, **kwargs)
        return canvas

    def __call__(self, **kwargs):  # Create a new copy of this design with some settings
        kwa = {key: value.get(self) for key, value in self.properties().items()}
        kwa.update(kwargs)
        new = type(self)(self.instructions, **kwa)
        return new


__all__ = ["read_design_from", "Design", "format_value"]
