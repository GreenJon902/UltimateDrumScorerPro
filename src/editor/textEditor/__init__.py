from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout

from assembler.pageContent.text import Text

Builder.load_file("editor/textEditor/textEditor.kv")

Image
class TextEditor(RelativeLayout):
    text_instance: Text

    def __init__(self, text_instance, **kwargs):
        self.text_instance = text_instance

        RelativeLayout.__init__(self, **kwargs)

    def set_text(self, _, value):
        self.text_instance.text = value
