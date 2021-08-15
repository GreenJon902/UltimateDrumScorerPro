from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from logger import ClassWithLogger


class SliderWithText(BoxLayout, ClassWithLogger):
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


    def validate_text(self):
        text = self.ids["text_input"].text
        self.log_dump(f"Validating text - \"{text}\"")

        fl: list[str] = list()

        for char in text:
            if char in ([str(n) for n in range(0, 9)] + ["."]):
                fl.append(char)

        fs = "".join(fl)
        if fs == "":
            self.log_dump(f"Got nothing or just text, clearing")
            self.ids["text_input"].text = fs

        else:
            self.value = float(fs)  # Dont have to set text input because slider can link that back to text input
            self.log_dump(f"Got - {fs}")


    def normalize(self, value):
        if value < self.min:
            return self.min

        elif value > self.max:
            return self.max

        else:
            return round(value, 2)