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
    notePains: list[list[NotePainElement]] = [
        [
            NotePainElement(pos=("0cm", "0cm"), size=("0.5cm", "0.25cm"), color=(0, 0, 0), symbol="tilted_line")
        ]
    ]
    currentNotePain = 0

    line_thickness: int = metrics.cm(0.1)



__all__ = ["Config"]
