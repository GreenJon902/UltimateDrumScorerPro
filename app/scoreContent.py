from io import BytesIO

from PIL import Image as PilImage, ImageDraw as PilImageDraw, ImageFont as PilImageFont
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.image import Texture
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput

from app import metrics
from app.popups import AddTextPopup
from logger.classWithLogger import ClassWithLogger


class ScoreContent(RelativeLayout, ClassWithLogger):
    def __init__(self, location_to_put, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.pos_hint = location_to_put

        self.size_hint = None, None


class Text(ScoreContent):
    text: str = StringProperty("Text")
    font_size: float = NumericProperty(10)
    texture: Texture = ObjectProperty()
    update: callable


    def __init__(self, *args, **kwargs):
        ScoreContent.__init__(self, *args, **kwargs)

        self.popup()

        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())
        self.bind(text=lambda _instance, _value: self.update(), font_size=lambda _instance, _value: self.update())


    def _update(self):
        self.texture = text_to_core_image(text=self.text, font_size=self.font_size).texture


    def on_texture(self, _instance, value):
        self.ids["image"].texture = value
        self.size = value.size


    def popup(self):
        popup = AddTextPopup()
        popup.bind(on_dismiss=self.popup_finished)
        popup.open()


    def popup_finished(self, instance):
        self.text = instance.ids["text"].text
        self.font_size = int(metrics.MM.to_pt(instance.ids["font_size"].value))








def text_to_core_image(text, font_size, color=(0, 0, 0, 255)):
    im = PilImage.new("RGBA", metrics.page_size_px)

    fnt = PilImageFont.truetype("resources/arial.ttf", font_size)
    imDraw = PilImageDraw.Draw(im)
    imDraw.text((0, 0), text, fill=color, font=fnt)

    imBbox = im.getbbox()
    imC = im.crop(imBbox)

    data = BytesIO()
    imC.save(data, format="png")
    data.seek(0)

    kvImg = CoreImage(BytesIO(data.read()), ext="png")
    return kvImg


