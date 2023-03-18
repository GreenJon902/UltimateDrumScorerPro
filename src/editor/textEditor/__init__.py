from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput

from assembler.pageContent.text import Text

Builder.load_file("editor/textEditor/textEditor.kv")


class TextEditor(RelativeLayout):
    text_instance: Text
    text_input: TextInput

    def __init__(self, text_instance, **kwargs):
        self.text_instance = text_instance

        holder = BoxLayout()
        self.text_input = TextInput(text=text_instance.text)
        holder.add_widget(self.text_input)

        RelativeLayout.__init__(self, **kwargs)
        self.add_widget(holder)
        self.text_input.bind(text=self.update_text)

    def update_text(self, _, value):
        self.text_instance.text = value

