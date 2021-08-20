from fractions import Fraction
from math import log

from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.graphics import Canvas, Rectangle, Line
from kivy.input import MotionEvent

from app.graphicsConstants import note_width, note_head_width, staff_gap, note_stem_width, note_stem_height, \
    staff_height, note_flag_dpos, note_flag_gap
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup
from app_info.score_info import next_notes_char, note_name_to_staff_level, next_note_char, duration_to_text_duration

rest_textures = Atlas("resources/atlases/rests.atlas").textures
note_head_textures = Atlas("resources/atlases/note_heads.atlas").textures



class Section(ScoreContentWithPopup):
    update: callable

    required_mode = "section"

    notes = "4[kick,snare snare kick kick,snare snare . snare kick snare snare . kick . . kick .]"

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
        self.note_canvas.__enter__()


        notes_per_beat = int(self.notes[0:self.notes.find("[")])
        _all_notes = [([note for note in notes.split(next_note_char)])
                      for notes in str(self.notes[self.notes.find("[") + 1:self.notes.find("]")]).split(next_notes_char)
                      ]

        all_notes = [_all_notes[n:n+4] for n in range(0, len(_all_notes), notes_per_beat)]
        self.log_debug(f"Got notes_per_beat: {notes_per_beat}, all_notes: {all_notes}")
        self.log_dump()
        dx = 0
        beat_index = 0

        for beat in all_notes:
            self.log_dump()
            self.log_debug(f"Beat {beat_index} --------------| notes: {beat} |--------------")
            amount_of_beat_done = 0
            had_not_rest_this_beat = False


            for notes in beat:
                self.log_dump(f"notes: {notes}, amount_of_beat_done: {amount_of_beat_done}, dx: {dx}")
                did_do_a_draw = False

                amount_of_beat_done += Fraction(1, notes_per_beat)


                # Drawing note bodies -----------------------
                if notes == ["."]:
                    if not had_not_rest_this_beat:
                        draw_note(f"{duration_to_text_duration[notes_per_beat]}_rest", dx * note_width)
                        did_do_a_draw = True


                else:
                    for note in notes:
                        draw_note(note, dx * note_width)
                        did_do_a_draw = True
                        had_not_rest_this_beat = True



                if did_do_a_draw:
                    dx += 1







            beat_index += 1

        self.log_dump()
        self.width = len(self.notes.split(next_notes_char)) * note_width


        self.note_canvas.__exit__()



def draw_note(note_name, x):
    note_shape = note_name

    if note_name in ["kick", "snare"]:
        note_shape = "circle"


    if note_shape in rest_textures.keys():
        Rectangle(pos=(x, 0), size=(note_width, staff_height),
                  texture=rest_textures[note_shape])


    elif note_shape in note_head_textures.keys():
        Rectangle(pos=(x, note_name_to_staff_level[note_name] * staff_gap),
                  size=(note_head_width, staff_gap),
                  texture=note_head_textures[note_shape])


def draw_beat(beat_notes):



    for note_name in beat_notes:
        if note_name == ".":
            print(amount_of_beat_done)


        else:
            draw_note()




    # Stems, Bars, Flags -----------------------------------------------------------------------------------------------
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
            flags = note_duration_to_bar_or_flag_amount(d)
            for flag_index in range(flags):
                Line(points=(x,
                             y + (note_flag_gap * flag_index),
                             x + note_flag_dpos[0],
                             y + note_flag_dpos[1] + (note_flag_gap * flag_index)),
                     width=note_stem_width)

        else:  # No special barring method available, will just do a flat one at highest point
            highest = max([values[1] for values in stem_start_points_since_last_beat])

            for n_index, (x, y, d) in enumerate(stem_start_points_since_last_beat):  # Stems
                with self.note_canvas:
                    Line(points=(x, y, x, highest + note_stem_height), width=note_stem_width)

                    if n_index < (len(stem_start_points_since_last_beat) - 1) and \
                            (x != stem_start_points_since_last_beat[n_index + 1][0]):
                        flags = note_duration_to_bar_or_flag_amount(
                            Fraction(1, min((d.denominator,
                                             stem_start_points_since_last_beat[n_index + 1][
                                                 2].denominator))))
                        print("f", flags)
                        for flag_index in range(flags):
                            y_offset = flag_index * note_flag_gap * -1

                            Line(points=(x,
                                         highest + note_stem_height + y_offset,
                                         stem_start_points_since_last_beat[n_index + 1][0],
                                         highest + note_stem_height + y_offset),
                                 width=note_stem_width)

        amount_of_beat_done = 0
        stem_start_points_since_last_beat.clear()




def note_duration_to_bar_or_flag_amount(fraction: Fraction):  # denominator = 2^n
    denominator = fraction.denominator

    # 2^n = denominator
    # log(2^n) = log(denominator)
    # n* (log(2)) = log(denominator)
    # n = log(denominator) / log(2)    <------ is what we need to do



    # if denominator = 8

    # 2^n = 8
    # log(2^n) = log(8)
    # n* (log(2)) = log(8)
    # n = log(8) / log(2)
    # n = 3

    n = log(denominator) / log(2)

    # if n is 1.0 or 2.0 then int(n) == 1 or 2 which still == n, but if it is 1.5 then it doesnt == int(n) which is 2
    assert n == int(n), f"note_duration_to_bar_or_flag_amount has too " \
                        f"take a fraction that has a denominator that is 1, 2, 4, 8...  not {fraction.denominator}"
    return int(n)

