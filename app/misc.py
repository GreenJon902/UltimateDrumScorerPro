import re

from kivy.properties import BoundedNumericProperty, NumericProperty, StringProperty, AliasProperty
from kivy.uix.boxlayout import BoxLayout


class SliderWithText(BoxLayout):
    min: int = NumericProperty(0)
    max: int = NumericProperty(10)

    value: float = NumericProperty(0)
    value_normalized: int

    hint_text: str = StringProperty()


    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        self.value_normalized = self.normalize(self.value)


    def on_value(self, _instance, value):
        self.value_normalized = self.normalize(value)

        self.ids["text_input"].text = str(self.value_normalized)
        self.ids["slider"].value = self.value_normalized


    def get(self):
        self.validate_text()
        return self.value_normalized


    def validate_text(self):
        text = self.ids["text_input"].text

        fl: list[str] = list()

        for char in text:
            if char in ([str(n) for n in range(0, 9)] + ["."]):
                fl.append(char)

        fs = "".join(fl)
        if fs == "":
            self.ids["text_input"].text = fs

        else:
            self.value = float(fs)


    def normalize(self, value):
        if value < self.min:
            return self.min

        elif value > self.max:
            return self.max

        else:
            return round(value, 2)
