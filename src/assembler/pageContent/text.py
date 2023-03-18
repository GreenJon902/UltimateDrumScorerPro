from kivy.clock import Clock
from kivy.clock import Clock
from kivy.core.image import Texture
from kivy.properties import ColorProperty, StringProperty, ObjectProperty, NumericProperty

from assembler.pageContent import PageContent
from markdownLabel import CoreMarkdownLabel


class Text(PageContent):
    text: str = StringProperty(defaultvalue="Text")
    color = ColorProperty(defaultvalue=(0, 0, 0, 1))
    font_size: float = NumericProperty(defaultvalue=10)  # height of small characters in mm

    label: CoreMarkdownLabel = ObjectProperty()
    texture: Texture = ObjectProperty()

    def __init__(self, *args, **kwargs):
        self.trigger_texture = Clock.create_trigger(self._texture_update, -1)
        self.label = CoreMarkdownLabel(text=self.text, color=self.color, font_size=self.font_size)

        PageContent.__init__(self, *args, **kwargs)

        self.bind(text=self.trigger_texture, color=self.trigger_texture, font_size=self.trigger_texture)

        Clock.schedule_once(self.trigger_texture, 0)

    def _texture_update(self, *args):
        # So font draws at correct resolution we multiply by the amount that this widget has been zoomed in on
        zoom_amount = (self.to_window(0, 1)[1] - self.to_window(0, 0)[1])

        self.label.text = self.text
        self.label.options["color"] = self.color
        self.label.options["font_size"] = self.font_size * zoom_amount

        self.label.refresh()
        self.label.texture.bind()
        self.size = self.label.texture.size[0] / zoom_amount, self.label.texture.size[1] / zoom_amount
        self.texture = self.label.texture
