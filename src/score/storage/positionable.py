from kivy.properties import NumericProperty, ReferenceListProperty


class Positionable:
    x: int = NumericProperty(0)
    y: int = NumericProperty(0)
    pos: list[int] = ReferenceListProperty(x, y)
