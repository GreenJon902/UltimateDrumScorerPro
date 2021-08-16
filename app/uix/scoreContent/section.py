from kivy.clock import Clock
from kivy.graphics import Canvas, Translate
from kivy.input import MotionEvent

from app.graphicsConstants import note_width
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.note import Note
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup


class Section(ScoreContentWithPopup):
    update: callable

    required_mode = "section"
    notes = list([Note(name="quarter_rest"), Note(name="bass"), Note(name="snare")])

    note_canvas: Canvas

    def get_popup_class(self, **kwargs):
        return AddSectionPopup(**kwargs)

    def popup_submitted(self, instance, data):
        self.update()

    def __init__(self, **kwargs):
        ScoreContentWithPopup.__init__(self, **kwargs)

        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())
        self.note_canvas = Canvas()
        self.canvas.add(self.note_canvas)

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
        self.note_canvas.clear()

        for n, note in enumerate(self.notes):
            if note == "rest":
                note = "quarter_rest"  # TODO: Correct rest types

            self.note_canvas.add(note.canvas)
            self.note_canvas.add(Translate(note_width, 0, 0))

        self.width = len(self.notes) * note_width
