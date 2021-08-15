from io import BytesIO
from typing import Optional

from PIL import Image as PilImage, ImageDraw as PilImageDraw, ImageFont as PilImageFont
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.image import Texture
from kivy.input import MotionEvent
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout

from app import metrics
from app.graphicsConstants import minimum_mouse_move_for_score_content_to_not_be_a_click, note_width
from app.misc import check_mode
from app.popups import AddTextPopup, AddSectionPopup
from logger import ClassWithLogger


class ScoreContent(RelativeLayout, ClassWithLogger):
    click_current_uid: Optional[int] = None
    required_mode = None


    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.size_hint = None, None


    def on_touch_down(self, touch: MotionEvent):
        if self.collide_point(*touch.pos) and check_mode(self.required_mode):
            self.click_current_uid = touch.uid


    def on_touch_move(self, touch: MotionEvent):
        if touch.uid == self.click_current_uid:
            self.x += touch.dx
            self.y += touch.dy


    def on_touch_up(self, touch: MotionEvent):
        if touch.uid == self.click_current_uid:
            self.click_current_uid = None
            return True
        return False





class ScoreContentWithPopup(ScoreContent):
    is_active = False  # For cancel - true if has been submitted at least once

    def on_touch_up(self, touch: MotionEvent):
        s = minimum_mouse_move_for_score_content_to_not_be_a_click

        if touch.uid == self.click_current_uid:
            if ((s * -1) <= touch.dx <= s) and ((s * -1) <= touch.dy <= s):

                # Get start pos since shouldn't have moved---
                x, y = touch.pos
                ox, oy = touch.opos

                tdx = ox - x
                tdy = oy - y

                self.x += tdx
                self.y += tdy
                # -------------------------------------------

                self.popup(text=self.text, font_size=metrics.PT.to_mm(self.font_size))

            self.click_current_uid = None
            return True

        return False


    def __init__(self, **kwargs):
        ScoreContent.__init__(self, **kwargs)

        self.popup()

    def popup(self, **kwargs):
        self.log_debug("Creating popup to edit text")
        popup = self.get_popup_class(**kwargs)
        popup.bind(on_submitted=self.popup_submitted, on_cancelled=self.popup_cancelled)
        popup.open()

    def _popup_submitted(self, instance, data):
        self.log_dump(f"Popup submitted, data - {data}")
        self.popup_submitted(instance, data)


    def popup_cancelled(self, _instance):
        if not self.is_active:
            self.log_dump("Popup cancelled but was already text so not removing")

            self.parent.remove_widget(self)

        else:
            self.log_dump("Popup cancelled")



    def get_popup_class(self, **kwargs):
        raise NotImplementedError("No get_popup_class method implemented")


    def popup_submitted(self, instance, data):
        raise NotImplementedError("No popup_submitted method implemented")






class Text(ScoreContentWithPopup):
    required_mode = "text"

    def get_popup_class(self, **kwargs):
        return AddTextPopup(**kwargs)


    def popup_submitted(self, instance, data):
        self.text = data.pop("text")
        self.font_size = metrics.MM.to_pt(data.pop("font_size"))

        self.is_active = True


    text: str = StringProperty("Text")
    font_size: float = NumericProperty(10)
    texture: Texture = ObjectProperty()
    update: callable


    def __init__(self, **kwargs):
        ScoreContentWithPopup.__init__(self, **kwargs)

        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())
        self.bind(text=lambda _instance, _value: self.update(), font_size=lambda _instance, _value: self.update())


    def _update(self):
        self.log_dump("Updating texture...")
        # FIXME: Bug where text is displayed 10 too small, probably to do with metrics
        self.texture = text_to_core_image(text=self.text, font_size=self.font_size * 10).texture
        self.log_dump("Updated texture")


    def on_texture(self, _instance, value):
        self.ids["image"].texture = value
        self.size = value.size



class Section(ScoreContentWithPopup):
    update: callable

    required_mode = "section"
    notes = list(["rest", "rest", "rest", "rest"])

    def get_popup_class(self, **kwargs):
        return AddSectionPopup(**kwargs)

    def popup_submitted(self, instance, data):
        self.update()

    def __init__(self, **kwargs):
        ScoreContentWithPopup.__init__(self, **kwargs)

        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())

    def on_touch_up(self, touch: MotionEvent):
        if self.collide_point(*touch.pos):
            if check_mode("note"):
                ret = True

                self.update()

            else:
                ret = ScoreContentWithPopup.on_touch_up(*touch.pos)

            return ret
        return False


    def _update(self):
        self.clear_widgets()

        for n, note in enumerate(self.notes):
            if note == "rest":
                note = "quarter_rest"  # TODO: Correct rest types

            self.add_widget(Image(source=f"atlas://resources/atlases/notes/{note}",
                                  width=note_width,
                                  size_hint_x=None,
                                  x=note_width * n))

        self.width = len(self.notes) * note_width


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


