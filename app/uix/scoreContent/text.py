from kivy.clock import Clock
from kivy.core.image import Texture
from kivy.properties import StringProperty, NumericProperty, ObjectProperty

from app import metrics
from app.popups.addTextPopup import AddTextPopup
from app.uix.scoreContent import text_to_core_image
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup


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
