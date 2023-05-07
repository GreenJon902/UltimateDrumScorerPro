from kivy.properties import NumericProperty, ReferenceListProperty


class Positionable:
    """
    A nice little utility class that sets up x, y and makes the position list too.
    """

    x: int = NumericProperty(0)
    y: int = NumericProperty(0)
    pos: list[int] = ReferenceListProperty(x, y)


__all__ = ["Positionable"]
