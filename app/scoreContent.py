from io import BytesIO

from PIL import Image as PilImage, ImageDraw as PilImageDraw
from kivy.core.image import Image as CoreImage
from kivy.core.image import Texture
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput

from logger.classWithLogger import ClassWithLogger


class ScoreContent(RelativeLayout, ClassWithLogger):
    def __init__(self, location_to_put, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.pos_hint = location_to_put

        self.size_hint = None, None


class Text(ScoreContent):
    page_related_x: int = NumericProperty(5)
    page_related_y: int = NumericProperty(1)
    text: str = StringProperty("Text")
    texture: Texture = ObjectProperty()


    def __init__(self, *args, **kwargs):
        ScoreContent.__init__(self, *args, **kwargs)

        self.popup()



    def on_text(self, _instance, value):
        self.texture = text_to_core_image(value).texture


    def on_texture(self, _instance, value):
        self.ids["image"].texture = value
        self.size = value.size


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







def text_to_core_image(text, color=(0, 0, 0, 255)):
    im = PilImage.new("RGBA", (1000, 1000))
    imDraw = PilImageDraw.Draw(im)
    imDraw.text((0, 0), text, fill=color)
    imBbox = im.getbbox()
    imC = im.crop(imBbox)

    data = BytesIO()
    imC.save(data, format="png")
    data.seek(0)

    kvImg = CoreImage(BytesIO(data.read()), ext="png")
    return kvImg


