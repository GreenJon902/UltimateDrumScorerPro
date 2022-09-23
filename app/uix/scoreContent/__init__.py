from io import BytesIO
from typing import Optional

from PIL import Image as PilImage, ImageFont as PilImageFont, ImageDraw as PilImageDraw
from kivy.core.image import Image as CoreImage
from kivy.input import MotionEvent
from kivy.uix.relativelayout import RelativeLayout

from app import metrics
from app.misc import check_mode
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
