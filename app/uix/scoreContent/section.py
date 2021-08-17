from fractions import Fraction

from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.graphics import Canvas, Rectangle, Line
from kivy.input import MotionEvent

from app.graphicsConstants import note_width, note_head_width, staff_gap, note_stem_width, note_stem_height, \
    staff_height, note_flag_dpos, note_flag_gap
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
        stem_start_points_since_last_beat = list()
        amount_of_beat_done = 0
        dx = 0

        while note_index < len(nis):
            note_info = nis[note_index]

            duration_s, names_s = note_info.split(note_duration_and_note_names_splitter_char)
            names = names_s.split(note_name_splitter_char)
            duration = Fraction(duration_s)

            amount_of_beat_done += duration

            print(duration.__repr__(), duration_s, names, amount_of_beat_done, dx)


            with self.note_canvas:

                for name in names:
                    note_name = name

                    if name == "rest":
                        note_name = "quarter_rest"  # TODO: More correct rest system
                    if name in ["kick", "snare"]:
                        note_name = "circle"


                    if note_name in special_note_textures.keys():
                        Rectangle(pos=(dx, 0), size=(note_width, staff_height),
                                  texture=special_note_textures[note_name])


                    elif note_name in note_head_textures.keys():
                        Rectangle(pos=(dx, note_name_to_staff_level[name] * staff_gap),
                                  size=(note_head_width, staff_gap),
                                  texture=note_head_textures[note_name])

                        stem_start_points_since_last_beat.append((dx + note_head_width - (note_stem_width / 2),
                                                                  (note_name_to_staff_level[name] * staff_gap) +
                                                                        (staff_gap / 2),
                                                                  duration))



                assert amount_of_beat_done <= 1, "Somehow amount_of_beat_done was over 1"

                if amount_of_beat_done == 1:
                    print("aobd == 1     ", stem_start_points_since_last_beat)


                    if len(stem_start_points_since_last_beat) == 0:  # Rest
                        pass

                    elif len(stem_start_points_since_last_beat) == 1:
                        x, y, d = stem_start_points_since_last_beat[0]

                        with self.note_canvas:
                            Line(points=(x, y, x, y + note_stem_height), width=note_stem_width)


                        # UNTESTED: Flags for single notes
                        flags = (1 / d / 2) if d != 1 else 0  # no flags if its a crochet
                        for flag_index in range(flags):
                            Line(points=(x,
                                         y + (note_flag_gap * flag_index),
                                         x + note_flag_dpos[0],
                                         y + note_flag_dpos[1] + (note_flag_gap * flag_index)),
                                 width=note_stem_width)



                    amount_of_beat_done = 0
                    stem_start_points_since_last_beat.clear()


            note_index += 1
            dx += note_width


        self.width = len(self.note_infos.split(next_notes_char)) * note_width
