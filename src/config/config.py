from kivy import metrics
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty, ColorProperty, DictProperty


class NotePainElement(EventDispatcher):
    x = NumericProperty()
    y = NumericProperty()
    pos = ReferenceListProperty(x, y)

    width = NumericProperty()
    height = NumericProperty()
    size = ReferenceListProperty(width, height)

    color = ColorProperty()
    thickness = NumericProperty()

    symbol: str = StringProperty()


class Config:
    notePains: list[list[NotePainElement]] = [[
        NotePainElement(pos=("0cm", "-1cm"), size=("0.5cm", "0.4cm"), color=(0, 0, 0), symbol="oval_with_tilted_line"), # Tom 1
        NotePainElement(pos=("0cm", "-0.6cm"), size=("0.5cm", "0.4cm"), color=(0, 0, 0), symbol="oval_with_tilted_line"),  # Tom 2
        NotePainElement(pos=("0cm", "0cm"), size=("0.5cm", "0.25cm"), color=(0, 0, 0), symbol="tilted_line"),  # Snare
        NotePainElement(pos=("0cm", "0.4cm"), size=("0.5cm", "0.4cm"), color=(0, 0, 0), symbol="oval_with_tilted_line"),  # Tom 3
    ]]
    currentNotePain = 0

    line_thickness: int = metrics.cm(0.05)


__all__ = ["Config"]
