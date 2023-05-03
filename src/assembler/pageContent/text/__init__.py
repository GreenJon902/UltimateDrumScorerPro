from kivy.core.image import Texture
from kivy.core.image import Texture
from kivy.properties import ObjectProperty

from assembler.pageContent import PageContent
from markdownLabel import CoreMarkdownLabel
from score import TextStorage


class Text(PageContent):
    storage: TextStorage
    label: CoreMarkdownLabel = ObjectProperty()
    texture: Texture = ObjectProperty()
