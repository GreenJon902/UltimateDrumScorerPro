from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout

Builder.load_file("score/bar.kv")


class Bar(RelativeLayout):
    line_height: int = NumericProperty()
