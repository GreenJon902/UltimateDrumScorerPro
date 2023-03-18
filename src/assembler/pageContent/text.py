from kivy.properties import ColorProperty, StringProperty
from kivy.uix.label import Label

from assembler.pageContent import PageContent
from markdownLabel import MarkdownLabel


class Text(PageContent):
    text: str = StringProperty(defaultvalue="Text")
    color = ColorProperty(defaultvalue=(0, 0, 0, 1))

    label: Label

    def __init__(self, *args, **kwargs):
        self.label = MarkdownLabel(text=self.text, color=self.color)
        PageContent.__init__(self, *args, **kwargs)
        self.size_hint = None, None
        self.add_widget(self.label)
        self.label.bind(texture_size=self.set_size)

    def on_text(self, _, value):
        self.label.text = value

    def on_color(self, _, value):
        self.label.color = value

    def set_size(self, _, size):
        self.size = size
