from betterLogger import ClassWithLogger
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout


class NewSectionButton(RelativeLayout, ClassWithLogger):
    transparency: int = NumericProperty()

    def __init__(self, size, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.size = size
        self.size_hint = None, None

        with self.canvas:
            self.color = Color(rgb=(0.5, 1, 0.5), a=self.transparency)
            RoundedRectangle(pos=self.pos, size=self.size)


    def on_transparency(self, _, a):
        self.color.a = a
