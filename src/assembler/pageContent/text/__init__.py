from kivy.core.image import Texture
from kivy.core.image import Texture
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty

from assembler.pageContent import PageContent
from markdownLabel import CoreMarkdownLabel


class Text(PageContent):
    text: str = StringProperty(defaultvalue="Text")
    font_size: float = NumericProperty(defaultvalue=10)  # height of small characters in mm
    do_markup: bool = BooleanProperty(defaultvalue=True)  # height of small characters in mm

    label: CoreMarkdownLabel = ObjectProperty()
    texture: Texture = ObjectProperty()
