from fractions import Fraction
from math import log

from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.graphics import Canvas, Rectangle, Line
from kivy.input import MotionEvent

from app.graphicsConstants import note_width, note_head_width, staff_gap, staff_height, note_stem_width, \
    note_stem_height, note_flag_gap
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

    notes = "4[snare kick . kick kick kick . . . . kick snare . snare snare .]"

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
        beat_end_dx_list = list([0])
        draw_notes_indexes_this_beat = list()
        note_stem_top_and_duration = list()

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
                self.log_dump(f"\b[Notes and Rests]  values: ({notes}, amount_of_beat_done: {amount_of_beat_done}, dx: "
                              f"{dx}, sub_beats_to_skip: {sub_beats_to_skip})")
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

            self.log_dump(f"\b[Bars and Flags ]  Sorted note_stem_anchor_points_and_their_note_indexes, got "
                          f"{anchors_with_indexes} from {note_positions_with_indexes}")"""

            music_notes = [notes for notes in beat if notes != ["."]]
            self.log_dump(f"\b[Bars and Flags ]  There are {len(music_notes)} sub beats, looking for special rule")


            # TODO: Multiple bars
            # Two Notes --------------
            if len(music_notes) == 0:
                self.log_dump("\b[Bars and Flags ]  No music notes written / only rests  so no need for Bars or Flags")

            elif len(music_notes) == 2:

                note_poses = list()
                note_indexes = list()
                sx = 0
                for note_index, notes in enumerate(beat):
                    if notes != ["."]:
                        note_poses.append((
                            (sx * note_width) + note_head_width - note_stem_width + (beat_end_dx_list[-2] * note_width),
                            min([note_name_to_staff_level[note_name] for note_name in notes]
                                ) * staff_gap + (staff_gap / 2)
                        ))
                        note_indexes.append(note_index)

                    if note_index in draw_notes_indexes_this_beat:
                        sx += 1

                note_1_pos, note_2_pos = note_poses
                note_1_index, note_2_index = note_indexes
                self.log_dump(f"\b[Bars and Flags ]  Special rule found, positions are {note_1_pos, note_2_pos}")

                Line(points=(*note_1_pos, note_1_pos[0], note_1_pos[1] + note_stem_height), width=note_stem_width)
                Line(points=(*note_2_pos, note_2_pos[0], note_2_pos[1] + note_stem_height), width=note_stem_width)



                note_stem_top_and_duration.append(((note_1_pos[0], note_1_pos[1] + note_stem_height),
                                                   get_note_duration(beat, note_1_index, notes_per_beat)))
                note_stem_top_and_duration.append(((note_2_pos[0], note_2_pos[1] + note_stem_height),
                                                   get_note_duration(beat, note_2_index, notes_per_beat)))




            # More ----------------------
            else:
                self.log_dump(f"\b[Bars and Flags ]  No special rule found")
                highest_point = max([max([(note_name_to_staff_level[note_name] if note_name != "." else 0)
                                          for note_name in notes])
                                     for notes in beat]) * staff_gap + (staff_gap / 2)

                note_poses = list()
                sx = 0
                for note_index, notes in enumerate(beat):
                    if notes != ["."]:
                        note_poses.append((
                            (sx * note_width) + note_head_width - note_stem_width + (beat_end_dx_list[-2] * note_width),
                            min([note_name_to_staff_level[note_name] for note_name in notes]
                                ) * staff_gap + (staff_gap / 2)
                        ))

                        note_stem_top_and_duration.append(((
                                (sx * note_width) + note_head_width - note_stem_width + (beat_end_dx_list[-2] *
                                                                                         note_width),
                                highest_point + note_stem_height),
                            get_note_duration(beat, note_index, notes_per_beat)
                        ))


                    if note_index in draw_notes_indexes_this_beat:
                        sx += 1

                for note_pos in note_poses:
                    Line(points=(*note_pos, note_pos[0], highest_point + note_stem_height), width=note_stem_width)



            # ----------------------------

            self.log_dump(f"\b[Bars and Flags ]  Bar positions and not durations: {note_stem_top_and_duration}")
            for note_index in range(len(note_stem_top_and_duration) - 1):
                if note_index < len(note_stem_top_and_duration) - 1:

                    stem_top_pos, duration = note_stem_top_and_duration[note_index]
                    next_stem_top_pos, next_duration = note_stem_top_and_duration[note_index + 1]

                    print(stem_top_pos, next_stem_top_pos)
                    print(duration, next_duration)

                    if duration >= next_duration:
                        for bar_index in range(note_duration_to_bar_or_flag_amount(duration)):
                            Line(points=(stem_top_pos[0],
                                         stem_top_pos[1] - (bar_index * note_flag_gap),
                                         next_stem_top_pos[0],
                                         next_stem_top_pos[1] - (bar_index * note_flag_gap)),
                                 width=note_stem_width)

                    else:
                        bar_index = 0

                        Line(points=(stem_top_pos[0],
                                     stem_top_pos[1],
                                     next_stem_top_pos[0],
                                     next_stem_top_pos[1]),
                             width=note_stem_width)

                        for bar_index in range(note_duration_to_bar_or_flag_amount(next_duration) - 1):
                            Line(points=(stem_top_pos[0],
                                         stem_top_pos[1] - (bar_index * note_flag_gap),
                                         next_stem_top_pos[0],
                                         next_stem_top_pos[1] - (bar_index * note_flag_gap)),
                                 width=note_stem_width)

                        bar_index += 1
                        Line(points=(stem_top_pos[0],
                                     stem_top_pos[1] - (bar_index * note_flag_gap),
                                     stem_top_pos[0] + ((next_stem_top_pos[0] - stem_top_pos[0]) / 2),
                                     next_stem_top_pos[1] - (bar_index * note_flag_gap) -
                                        ((next_stem_top_pos[1] - stem_top_pos[1]) / 2)),
                             width=note_stem_width)

            print()
            # ----------------------------
            note_positions_with_indexes.clear()
            draw_notes_indexes_this_beat.clear()
            note_stem_top_and_duration.clear()
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


def get_note_duration(beat, note_index, notes_per_beat):
    notes_after_note_index = beat[note_index + 1:len(beat)]

    i = 1
    for note in notes_after_note_index:
        if note != ["."]:
            break

        i += 1

    print(notes_after_note_index, i, beat, note_index)

    return Fraction(i, notes_per_beat)
