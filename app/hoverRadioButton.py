from kivy.properties import StringProperty
from kivy.uix.image import Image

from app.boxLayoutWithEvents import BoxLayoutWithClickHoverEvent


class HoverRadioButton(BoxLayoutWithClickHoverEvent):
    image: Image

    name: str = StringProperty()


    def __init__(self, **kwargs):
        BoxLayoutWithClickHoverEvent.__init__(self, **kwargs)

        self.image = Image()
        self.add_widget(self.image)


    def update_image(self):
        self.image.source = (f"resources/buttons/{self.name}_button_click.png" if self.state == "down"
                             else (f"resources/buttons/{self.name}_button_hover.png" if self.mouse_over
                                   else f"resources/buttons/{self.name}_button_normal.png"))
