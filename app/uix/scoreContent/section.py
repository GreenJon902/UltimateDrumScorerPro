from kivy.clock import Clock
from kivy.input import MotionEvent
from kivy.uix.image import Image

from app.graphicsConstants import note_width
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup


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
