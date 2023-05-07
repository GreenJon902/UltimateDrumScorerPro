from kivy.properties import StringProperty, NumericProperty, BooleanProperty

from scoreStorage import ScoreStorageItem
from scoreStorage.positionable import Positionable


class TextStorage(ScoreStorageItem, Positionable):
    text: str = StringProperty(defaultvalue="Text")
    font_size: float = NumericProperty(defaultvalue=10)  # height of small characters in mm
    do_markup: bool = BooleanProperty(defaultvalue=True)  # height of small characters in mm

    def serialize(self) -> dict:
        return {
            "text": self.text,
            "font_size": self.font_size,
            "do_markup": self.do_markup,
            "pos": self.pos
        }

    @staticmethod
    def deserialize(serialized: dict[str, any]) -> "TextStorage":
        return TextStorage(**serialized)
