from fractions import Fraction

from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.graphics import Canvas, Translate, PushMatrix, PopMatrix, Rectangle, Line
from kivy.input import MotionEvent

from app.graphicsConstants import note_width, staff_height, note_head_width, staff_gap, note_stem_width
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup
from app_info.score_info import next_notes_char, note_duration_and_note_names_splitter_char, note_name_splitter_char, \
    note_name_to_staff_level

special_note_textures = Atlas("resources/atlases/special_notes.atlas").textures
note_head_textures = Atlas("resources/atlases/note_heads.atlas").textures



class Section(ScoreContentWithPopup):
    update: callable

    required_mode = "section"
    note_infos = "1-kick\n1-rest\n1/4-snare\n1/4-snare\n1/2-kick snare"  # For testing, Everything is x4 bc instead
    # of bar it is beat fraction

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


        nis = self.note_infos.split(next_notes_char)
        note_index = 0
        stem_top_points_since_last_beat = list()
        amount_of_beat_done = 0

        while note_index < len(nis):
            note_info = nis[note_index]

            duration_s, names_s = note_info.split(note_duration_and_note_names_splitter_char)
            names = names_s.split(note_name_splitter_char)
            duration = Fraction(duration_s)

            amount_of_beat_done += duration

            print(duration.__repr__(), duration_s, names, amount_of_beat_done)

            with self.note_canvas:
                PushMatrix()
                Translate(note_width * note_index, 0)

                for name in names:
                    note_name = name

                    if name == "rest":
                        note_name = "quarter_rest"  # TODO: More correct rest system
                    if name in ["kick", "snare"]:
                        note_name = "circle"


                    if note_name in special_note_textures.keys():
                        Rectangle(pos=(0, 0), size=(note_width, staff_height),
                                  texture=special_note_textures[note_name])


                    elif note_name in note_head_textures.keys():
                        PushMatrix()
                        Translate(0, note_name_to_staff_level[name] * staff_gap)


                        Rectangle(pos=(0, 0), size=(note_head_width, staff_gap),
                                  texture=note_head_textures[note_name])

                        stem_top_points_since_last_beat.append(
                            (note_name_to_staff_level[name] * staff_gap) + staff_height)

                        PopMatrix()
                PopMatrix()


                assert amount_of_beat_done <= 1, "Somehow amount_of_beat_done was over 1"

                if amount_of_beat_done == 1:
                    print("aobd == 1     ", stem_top_points_since_last_beat)

                    if len(stem_top_points_since_last_beat) == 0:  # Rest
                        pass

                    else:
                        with self.note_canvas:
                            if len(stem_top_points_since_last_beat) == 1:
                                PushMatrix()
                                Translate(note_width, stem_top_points_since_last_beat[0])

                                Line(points=(0, 0 - staff_height, 0, 0),
                                     width=note_stem_width)

                                PopMatrix()

                            else:  # More than 1
                                for n_index, stem_top_pos in enumerate(stem_top_points_since_last_beat):
                                    PushMatrix()
                                    Translate(note_width * n_index, stem_top_pos)

                                    Line(points=(0, 0 - staff_height, 0, 0),
                                         width=note_stem_width)

                                    PopMatrix()





                    amount_of_beat_done = 0
                    stem_top_points_since_last_beat.clear()


            note_index += 1


        self.width = len(self.note_infos.split(next_notes_char)) * note_width
