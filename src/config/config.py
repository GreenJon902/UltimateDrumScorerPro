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
    noteSelectorInfo: list[NotePainElement] = [
        NotePainElement(pos=("0cm", "0.4cm"), size=("0.5cm", "0.4cm"), symbol="oval_with_tilted_line"),  # Tom 1
        NotePainElement(pos=("0.25cm", "0cm"), size=("0.5cm", "0.5cm"), symbol="tilted_line"),  # Snare
        NotePainElement(pos=("-0.25cm", "0cm"), size=("0.5cm", "0.5cm"), symbol="tilted_line"),  # Snare
        NotePainElement(pos=("0cm", "-0.5cm"), size=("0.5cm", "0.4cm"), symbol="oval_with_tilted_line"),  # Tom 2
        NotePainElement(pos=("0cm", "-0.9cm"), size=("0.5cm", "0.4cm"), symbol="oval_with_tilted_line"),  # Tom 3
        NotePainElement(pos=("0cm", "-1.2cm"), size=("0.5cm", "0.5cm"), symbol="tilted_line"),  # Kick
    ]
    currentNotePain = 0

    line_thickness: int = metrics.cm(0.05)
    note_selector_uncommitted_color = (0, 0, 0, 0.3)
    note_selector_uncommitted_hover_color = (0.5, 0.5, 1, 1)
    note_selector_committed_hover_color = (1, 0.5, 0.5, 1)
    note_selector_distance = metrics.cm(0.5)

    note_color = (0, 0, 0, 1)


__all__ = ["Config"]
