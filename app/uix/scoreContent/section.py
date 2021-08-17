from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.graphics import Canvas
from kivy.input import MotionEvent

from app.graphicsConstants import note_width
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup

image_textures = Atlas("resources/atlases/notes.atlas").textures



class Section(ScoreContentWithPopup):
    update: callable

    required_mode = "section"
    note_infos = "1-2-3-4-5"

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

        for note_info in self.note_infos:
            pass


        self.width = len(self.notes) * note_width
