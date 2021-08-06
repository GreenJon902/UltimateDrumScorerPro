from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from logger.classWithLogger import ClassWithLogger


class ScoreContent(Widget, ClassWithLogger):
    draw: callable

    def __init__(self, location_to_put, **kwargs):
        Widget.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.pos_hint = location_to_put

        self.draw = Clock.create_trigger(lambda _elapsed_time: self._draw())

    def _draw(self):
        raise NotImplementedError("No draw function implemented")


class Text(ScoreContent):
    label: Label
    image: Image
    page_related_x: int = 5
    page_related_y: int = 1
    text: str = ""


    def __init__(self, *args, **kwargs):
        ScoreContent.__init__(self, *args, **kwargs)

        self.label = Label()
        self.image = Image()

        self.popup()


    def _draw(self):
        self.label.size = (self.page_related_x, self.page_related_y)
        self.label.text = self.text
        self.label.texture_update()

        self.image.texture = self.label.texture
        self.clear_widgets()
        self.add_widget(self.image)


    def popup(self):
        content = BoxLayout(orientation="vertical")
        textInput = TextInput(hint_text="Enter your text")
        textInput.name = "text"
        finishedButton = Button(text="Finish")
        finishedButton.name = "IGNORE"
        content.add_widget(textInput)
        content.add_widget(finishedButton)


        popup = Popup(title='Text',
                      content=content,
                      size_hint=(0.5, 0.5), auto_dismiss=False)
        finishedButton.bind(on_release=popup.dismiss)
        popup.bind(on_dismiss=self.popup_finished)
        popup.open()


    def popup_finished(self, instance):
        for child in instance.content.children:
            if hasattr(child, "name"):
                if child.name == "IGNORE":
                    pass

                elif child.name == "text":
                    self.text = child.text

                else:
                    self.log_warning("Widget with an unknown in popup, ignoring")

            else:
                self.log_warning("Widget with no name in popup, ignoring")
