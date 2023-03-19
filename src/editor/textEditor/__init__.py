from kivy.core.window import Window
from kivy.input import MotionEvent
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout

from assembler.pageContent.text import Text

Builder.load_file("editor/textEditor/textEditor.kv")


class TextEditor(RelativeLayout):
    text_instance: Text

    md_icon: Image = ObjectProperty()
    md_icon_hovered: bool = BooleanProperty()

    def __init__(self, text_instance, **kwargs):
        self.text_instance = text_instance

        RelativeLayout.__init__(self, **kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.bind(md_icon_hovered=self.do_md_icon_color)

    def set_text(self, _, value):
        self.text_instance.text = value

    def on_md_icon(self, _, value):
        if value is not None:
            self.text_instance.bind(do_markup=self.do_md_icon_color)
            self.md_icon.bind(enabled_color=self.do_md_icon_color, disabled_color=self.do_md_icon_color)


    def do_md_icon_color(self, *_):
        color = (
            (self.md_icon.enabled_hover_color if self.text_instance.do_markup else self.md_icon.disabled_hover_color)
            if self.md_icon_hovered else
            (self.md_icon.enabled_color if self.text_instance.do_markup else self.md_icon.disabled_color))
        if color is None:
            color = (1, 0, 0, 1)  # Just a placeholder
        self.md_icon.color = color

    def md_clicked(self, touch: MotionEvent):
        if touch is not None and self.md_icon.collide_point(touch.x, touch.y):
            self.text_instance.do_markup = not self.text_instance.do_markup


    def on_mouse_pos(self, _, value):
        value = self.md_icon.to_widget(*value)
        if self.md_icon.collide_point(value[0], value[1]):
            self.md_icon_hovered = True
        else:
            self.md_icon_hovered = False
