from fractions import Fraction
from math import log

from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.graphics import Canvas, Rectangle, Line
from kivy.input import MotionEvent

from app.graphicsConstants import note_width, note_head_width, staff_gap, staff_height, note_stem_width, \
    note_stem_height
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup
from app_info.score_info import next_notes_char, note_name_to_staff_level, next_note_char, duration_to_text_duration
from logger import push_name_to_logger_name_stack

rest_textures = Atlas("resources/atlases/rests.atlas").textures
note_head_textures = Atlas("resources/atlases/note_heads.atlas").textures



class Section(ScoreContentWithPopup):
    update: callable

    required_mode = "section"

    notes = "4[. . . . kick . snare . . . snare,kick .]"

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


    @push_name_to_logger_name_stack
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
        note_positions_with_indexes = list()
        beat_end_dx_list = list()
        draw_notes_indexes_this_beat = list()

        for beat in all_notes:
            self.log_dump()
            self.log_debug(f"Beat {beat_index} --------------| notes: {beat} |--------------")
            self.push_logger_name(f"beat_{beat_index}")
            amount_of_beat_done = 0
            had_not_rest_this_beat = False
            sub_beats_to_skip = 0

            # Drawing note bodies --------------------------------------------------------------------------------------
            for note_index, notes in enumerate(beat):
                self.push_logger_name(f"{note_index + 1}/{notes_per_beat}")
                self.log_dump(f"\b[Notes and Rests]  values: ({notes}, amount_of_beat_done: {amount_of_beat_done}, dx: {dx}, "
                              f"sub_beats_to_skip: {sub_beats_to_skip})")
                did_do_a_draw = False

                amount_of_beat_done += Fraction(1, notes_per_beat)

                if sub_beats_to_skip > 0:
                    sub_beats_to_skip -= 1

                else:
                    if notes == ["."]:
                        if not had_not_rest_this_beat:
                            did_do_a_draw = True

                            # Combining rests ----
                            if note_index < len(beat) - 1 and all([beat[note_index + n] == ["."] for n in range(1, 4)]):
                                sub_beats_to_skip = 3
                                draw_note(f"{duration_to_text_duration[notes_per_beat / 4]}_rest", dx * note_width)

                            elif note_index < len(beat) - 1 and beat[note_index + 1] == ["."]:
                                sub_beats_to_skip = 1
                                draw_note(f"{duration_to_text_duration[notes_per_beat / 2]}_rest", dx * note_width)

                            else:
                                draw_note(f"{duration_to_text_duration[notes_per_beat]}_rest", dx * note_width)

                    else:
                        for note in notes:
                            draw_note(note, dx * note_width)
                            did_do_a_draw = True
                            had_not_rest_this_beat = True




                if did_do_a_draw:
                    draw_notes_indexes_this_beat.append(note_index)
                    dx += 1

                self.pop_logger_name()
            beat_end_dx_list.append(dx)

            # Baring and flags -----------------------------------------------------------------------------------------
            """anchors_with_indexes = list()

            for n, (pos, note_index) in enumerate(note_positions_with_indexes):
                found = False

                for n2, (pos2, note_index2) in enumerate(note_positions_with_indexes):
                    if note_index == note_index2 and n != n2 and note_index:
                        found = True
                        to_add = ((pos[0], min((pos[1], pos2[1]))), note_index)

                        if to_add not in anchors_with_indexes:
                            anchors_with_indexes.append(to_add)


                if not found:
                    anchors_with_indexes.append(((pos[0], pos[1]), note_index))

            self.log_dump(f"\b[Bars and Tails ]  Sorted note_stem_anchor_points_and_their_note_indexes, got "
                          f"{anchors_with_indexes} from {note_positions_with_indexes}")"""

            music_notes = [notes for notes in beat if notes != ["."]]
            self.log_dump(f"\b[Bars and Tails ]  There are {len(music_notes)} sub beats, looking for special rule")



            # Two Notes --------------
            if len(music_notes) == 2:

                n_poses = list()
                sx = 0
                for note_index, notes in enumerate(beat):
                    if notes != ["."]:
                        n_poses.append((
                            (sx * note_width) + note_head_width - note_stem_width + (beat_end_dx_list[-2] * note_width),
                            min([note_name_to_staff_level[note_name] for note_name in notes]
                                ) * staff_gap + (staff_gap / 2)
                        ))

                    if note_index in draw_notes_indexes_this_beat:
                        sx += 1

                n1_pos, n2_pos = n_poses
                self.log_dump(f"\b[Bars and Tails ]  Special rule found, positions are {n1_pos, n2_pos}")

                Line(points=(*n1_pos, n1_pos[0], n1_pos[1] + note_stem_height), width=note_stem_width)
                Line(points=(*n2_pos, n2_pos[0], n2_pos[1] + note_stem_height), width=note_stem_width)

                Line(points=(n1_pos[0], n1_pos[1] + note_stem_height, n2_pos[0], n2_pos[1] + note_stem_height),
                     width=note_stem_width)



            note_positions_with_indexes.clear()
            self.pop_logger_name()
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
        return x, 0


    elif note_shape in note_head_textures.keys():
        Rectangle(pos=(x, note_name_to_staff_level[note_name] * staff_gap),
                  size=(note_head_width, staff_gap),
                  texture=note_head_textures[note_shape])
        return x, note_name_to_staff_level[note_name] * staff_gap





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

