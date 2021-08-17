from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.graphics import Canvas
from kivy.input import MotionEvent

from app.graphicsConstants import note_width
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup
from app_info.score_info import next_notes_char, note_duration_and_note_names_splitter_char, note_name_splitter_char

image_textures = Atlas("resources/atlases/notes.atlas").textures



class Section(ScoreContentWithPopup):
    update: callable

    required_mode = "section"
    note_infos = "1-kick\n1-rest\n1/4-snare\n1/4-snare\n1/2-kick snare"  # For testing

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
        print(self.note_infos, "\n")

        for note_info in self.note_infos.split(next_notes_char):
            duration, names_s = note_info.split(note_duration_and_note_names_splitter_char)
            names = names_s.split(note_name_splitter_char)

            print(duration, names)


        self.width = len(self.notes) * note_width
