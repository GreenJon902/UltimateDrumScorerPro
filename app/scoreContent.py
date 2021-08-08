from io import BytesIO

from PIL import Image as PilImage, ImageDraw as PilImageDraw, ImageFont as PilImageFont
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.image import Texture
from kivy.input import MotionEvent
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput

from app import metrics
from app.graphicsConstants import minimum_mouse_move_for_score_content_to_not_be_a_click
from app.popups import AddTextPopup
from logger.classWithLogger import ClassWithLogger


class ScoreContent(RelativeLayout, ClassWithLogger):
    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.size_hint = None, None


class Text(ScoreContent):
    text: str = StringProperty("Text")
    font_size: float = NumericProperty(10)
    texture: Texture = ObjectProperty()
    update: callable

    is_active = False  # For cancel - true if has been submitted at least once


    def __init__(self, **kwargs):
        ScoreContent.__init__(self, **kwargs)

        self.popup()

        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())
        self.bind(text=lambda _instance, _value: self.update(), font_size=lambda _instance, _value: self.update())


    def _update(self):
        # FIXME: Bug where text is displayed 10 too small, probably to do with metrics
        self.texture = text_to_core_image(text=self.text, font_size=self.font_size * 10).texture


    def on_texture(self, _instance, value):
        self.ids["image"].texture = value
        self.size = value.size


    def popup(self, **kwargs):
        popup = AddTextPopup(**kwargs)
        popup.bind(on_submitted=self.popup_submitted, on_cancelled=self.popup_cancelled)
        popup.open()


    def popup_submitted(self, _instance, data):
        self.text = data.pop("text")
        self.font_size = metrics.MM.to_pt(data.pop("font_size"))

        self.is_active = True


    def popup_cancelled(self, _instance):
        if not self.is_active:
            self.parent.remove_widget(self)


    def on_touch_down(self, touch: MotionEvent):
        if self.collide_point(*touch.pos):
            touch.grab(self)


    def on_touch_move(self, touch: MotionEvent):
        if touch.grab_current == self:
            self.x += touch.dx
            self.y += touch.dy


    def on_touch_up(self, touch: MotionEvent):
        s = minimum_mouse_move_for_score_content_to_not_be_a_click

        if touch.grab_current == self and ((s * -1) <= touch.dx <= s) and ((s * -1) <= touch.dy <= s):

            # Get start pos since shouldn't have moved---
            x, y = touch.pos
            ox, oy = touch.opos

            tdx = ox - x
            tdy = oy - y

            self.x += tdx
            self.y += tdy
            # -------------------------------------------

            self.popup(text=self.text, font_size=metrics.PT.to_mm(self.font_size))

            return True

        return False





def text_to_core_image(text, font_size, color=(0, 0, 0, 255)):
    im = PilImage.new("RGBA", metrics.page_size_px)

    font = PilImageFont.truetype("resources/arial.ttf", int(font_size))
    imDraw = PilImageDraw.Draw(im)
    imDraw.text((0, 0), text, fill=color, font=font)

    imBbox = im.getbbox()
    imC = im.crop(imBbox)

    data = BytesIO()
    imC.save(data, format="png")
    data.seek(0)

    kvImg = CoreImage(BytesIO(data.read()), ext="png")
    return kvImg


