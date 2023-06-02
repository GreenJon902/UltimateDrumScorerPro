from kivy.properties import NumericProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout

from kv import check_kv

check_kv()


class Decoration(RelativeLayout):
    min_height: int = NumericProperty()
    name: str = StringProperty()


__all__ = ["Decoration"]
