from typing import Union

from kivy.clock import Clock
from kivy.core.image import Texture
from kivy.core.text import Label as CoreLabel
from kivy.properties import StringProperty, ColorProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.uix.relativelayout import RelativeLayout

from markdownLabel import CoreMarkdownLabel


class BetterSizedLabel(RelativeLayout):
    text: str = StringProperty(defaultvalue="Text")
    color = ColorProperty(defaultvalue=(0, 0, 0, 1))
    font_size: float = NumericProperty(defaultvalue=10)  # height of small characters in mm
    do_markup: bool = BooleanProperty(defaultvalue=True)  # height of small characters in mm

    label: Union[CoreLabel, CoreMarkdownLabel] = ObjectProperty()
    texture: Texture = ObjectProperty()

    def __init__(self, **kwargs):
        self.trigger_texture = Clock.create_trigger(self._texture_update, -1)
        RelativeLayout.__init__(self, **kwargs)

        self.bind(text=self.trigger_texture, color=self.trigger_texture, font_size=self.trigger_texture,
                  do_markup=self.trigger_texture)

        self.trigger_texture()

    def on_do_markup(self, _, value):
        if value:
            self.label = CoreMarkdownLabel()
        else:
            self.label = CoreLabel()
        self.trigger_texture()

    def _texture_update(self, _):
        if self.label is None:
            self.on_do_markup(self, self.do_markup)

        # So font draws at correct resolution we multiply by the amount that this widget has been zoomed in on
        zoom_amount = (self.to_window(0, 1)[1] - self.to_window(0, 0)[1])

        self.label.text = self.text
        self.label.options["color"] = self.color
        self.label.options["font_size"] = self.font_size * zoom_amount
        self.label.do_markup = self.do_markup

        self.label.refresh()
        self.label.texture.bind()
        self.size = self.label.texture.size[0] / zoom_amount, self.label.texture.size[1] / zoom_amount
        self.texture = self.label.texture
