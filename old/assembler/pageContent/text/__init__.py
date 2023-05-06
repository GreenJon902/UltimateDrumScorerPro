from assembler.pageContent import PageContent
from kivy.core.image import Texture
from kivy.properties import ObjectProperty
from markdownLabel import CoreMarkdownLabel
from score import TextStorage


class Text(PageContent):
    storage: TextStorage
    label: CoreMarkdownLabel = ObjectProperty()
    texture: Texture = ObjectProperty()
