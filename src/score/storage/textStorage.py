from kivy.properties import StringProperty, NumericProperty, BooleanProperty

from score import ScoreStorageItem
from score.storage.positionable import Positionable


class TextStorage(ScoreStorageItem, Positionable):
    text: str = StringProperty(defaultvalue="Text")
    font_size: float = NumericProperty(defaultvalue=10)  # height of small characters in mm
    do_markup: bool = BooleanProperty(defaultvalue=True)  # height of small characters in mm
