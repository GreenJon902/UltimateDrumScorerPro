from fractions import Fraction
from math import log

from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.graphics import Canvas, Rectangle, Line, Ellipse
from kivy.input import MotionEvent
from kivy.properties import NumericProperty, OptionProperty, ListProperty, ReferenceListProperty
from kivy.uix.relativelayout import RelativeLayout

import constants
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup
from logger import push_name_to_logger_name_stack, ClassWithLogger, reset_logger_name_stack_for_function, \
    push_name_to_logger_name_stack_custom

rest_textures = Atlas("resources/atlases/rests.atlas").textures
note_head_textures = Atlas("resources/atlases/note_heads.atlas").textures


class Section(ScoreContentWithPopup, ClassWithLogger):
    notes: list = ListProperty()
    notes_per_beat = NumericProperty()

    time_signature_a: list = NumericProperty()
    time_signature_b: list = NumericProperty()
    time_signature: list = ReferenceListProperty(time_signature_a, time_signature_b)

    required_mode = "section"

    update = None
    
    def __init__(self, **kwargs):
        ClassWithLogger.__init__(self)
        ScoreContentWithPopup.__init__(self, **kwargs)

        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())

        self.time_signature, self.notes_per_beat, self.notes = self.parse_string("4/4-4[kick kick kick kick . kick . . "
                                                                                 "kick,snare . kick snare snare . kick "
                                                                                 " .]")


    def parse_string(self, string):
        parts = string.split("-")

        ts = parts[0].split("/")
        time_signature = int(ts[0]), int(ts[1])
        notes_per_beat = int(parts[1].split("[")[0])
        notes = [note.split(",") for note in parts[1].split("[")[1].replace("]", "").split(" ")]

        self.log_debug(f"Parsed {string} too ts={time_signature} npb={notes_per_beat} notes={notes}")
        return time_signature, notes_per_beat, notes


    @push_name_to_logger_name_stack
    def _update(self):
        beats_per_bar = self.notes_per_beat * self.time_signature[0]
        self.log_debug(f"{beats_per_bar} beats per bar")
        bars_needed = len(self.notes) / beats_per_bar

        # if bars_needed is 1.0 or 2.0 then int(bars_needed) == 1 or 2 which still == bars_needed,
        # but if it is 1.5 then it doesnt == int(bars_needed) which is 2
        assert bars_needed == int(bars_needed)

        bars_needed = int(bars_needed)
        bars_too_add = bars_needed - len(self.children)
        self.log_debug(f"Adding {bars_too_add} bar widgets too self from {bars_needed} out of {len(self.children)}")


        for _ in range(bars_too_add):
            b = Bar()
            b.bind(width=self.do_width)
            self.add_widget(b)

        for n, child in enumerate(self.children):
            notes = self.notes[n * beats_per_bar:(n + 1) * beats_per_bar]

            child.notes_per_beat = self.notes_per_beat
            child.notes = notes
            self.log_dump(f"Giving {child} \"{notes}\"")

        self.children[0].bar_start_line_type = "repeat"
        self.children[-1].bar_end_line_type = "repeat"


    def do_width(self, _instance, _value):
        width = 0
        for child in self.children:
            child.x = width
            width += child.width
        self.width = width




    def get_popup_class(self, **kwargs):
        return AddSectionPopup(**kwargs)

    def popup_submitted(self, instance, data):
        self.update()


    def on_touch_up(self, touch: MotionEvent):
        if check_mode("note") and self.collide_point(*touch.pos):
            pos = self.to_local(*touch.pos)

            note_position = int(((pos[0] - (pos[0] % constants.graphics.note_width)) /
                                    constants.graphics.note_width) + 1)

            self.log_dump(f"Adding note at {note_position}")

            a, b = self.notes.split("[")  # Fixme: update the function to work with the newer system
            notes = b.split(" ")
            notes[note_position] = ("kick" if notes[note_position] == "." else notes[note_position] + ",kick")

            self.notes = a + "[" + " ".join(notes)


        return ScoreContentWithPopup.on_touch_up(self, touch)



class Bar(RelativeLayout, ClassWithLogger):
    update: callable


    notes: list = ListProperty()
    notes_per_beat: int = NumericProperty()

    bar_start_line_type: str = OptionProperty("single", options=["single", "repeat"])
    bar_end_line_type: str = OptionProperty("single", options=["single", "repeat"])

    _bar_start_line_width: int = NumericProperty(constants.graphics.bar_edge_line_width)
    _bar_end_line_width: int = NumericProperty(constants.graphics.bar_edge_line_width)

    note_canvas: Canvas

    def __init__(self, **kwargs):
        ClassWithLogger.__init__(self)

        self.note_canvas = Canvas()
        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())
        self.bind(notes=lambda _instance, _value: self.update(), notes_per_beat=lambda _instance, _value: self.update())

        RelativeLayout.__init__(self, **kwargs)

        self.canvas.add(self.note_canvas)


    def on_bar_start_line_type(self, _instance, value):
        if value == "single":
            self._bar_start_line_width = constants.graphics.bar_edge_line_width

        elif value == "repeat":
            self._bar_start_line_width = constants.graphics.bar_edge_repeat_line_width

        else:
            self.log_critical(f"No know bar_start_line_type called {value}")


    def on_bar_end_line_type(self, _instance, value):
        if value == "single":
            self._bar_end_line_width = constants.graphics.bar_edge_line_width

        elif value == "repeat":
            self._bar_end_line_width = constants.graphics.bar_edge_repeat_line_width

        else:
            self.log_critical(f"No know bar_end_line_type called {value}")




    @push_name_to_logger_name_stack
    def _update(self):
        notes_per_beat = self.notes_per_beat

        all_notes = [self.notes[n:n + 4] for n in range(0, len(self.notes), notes_per_beat)]
        self.log_debug(f"Got notes_per_beat: {notes_per_beat}, all_notes: {all_notes}")
        self.log_dump()

        dx = 0


        self.note_canvas.clear()
        self.note_canvas.__enter__()


        for beat_index, beat_notes in enumerate(all_notes):
            self.log_dump()
            self.log_debug(f"Beat {beat_index + 1} --------------| notes: {beat_notes} |--------------")
            self.push_logger_name(f"beat_{beat_index}")

            sub_beats_to_skip, dx = self.draw_compressed_rests(beat_notes, dx)
            stem_y_points = self.get_stem_y_points(beat_notes)
            last_note_stem_y_points = None
            last_note_duration = None
            last_note_dx = None
            music_notes_draw_this_beat = 0

            for note_index, notes in enumerate(beat_notes):
                self.push_logger_name(f"{note_index + 1}/{notes_per_beat}")
                self.log_dump(f"values: ({notes}, amount_of_beat_done: "
                              f"{Fraction(note_index, notes_per_beat)}, dx: {dx}, sub_beats_to_skip: "
                              f"{sub_beats_to_skip})")

                note_duration = get_note_duration(beat_notes, note_index, notes_per_beat)

                if sub_beats_to_skip > 0:
                    sub_beats_to_skip -= 1

                else:
                    if notes == ["."]:
                        pass  # TODO: Rest width - For editing notes in gui, will expand bar probably

                    else:
                        note_stem_y_points = stem_y_points[music_notes_draw_this_beat]

                        for note in notes:
                            draw_note(note, dx)
                            Line(points=(dx + constants.graphics.note_head_width, note_stem_y_points[0],
                                         dx + constants.graphics.note_head_width, note_stem_y_points[1]),
                                 width=constants.graphics.note_stem_width)

                            if music_notes_draw_this_beat == 0 and all([sub_beat_notes == ["."]  # Flags required
                                                                        for sub_beat_notes in
                                                                        beat_notes[note_index + 1:len(beat_notes) - 1
                                                                                   ]]):
                                self.draw_note_flags(note_stem_y_points, note_duration, dx)

                            else:  # Bars required
                                if last_note_stem_y_points is not None:
                                    self.draw_note_bars(last_note_stem_y_points, last_note_duration, last_note_dx,
                                                        note_stem_y_points, note_duration, dx)

                        last_note_dx = dx
                        dx += constants.graphics.note_width
                        music_notes_draw_this_beat += 1

                        last_note_stem_y_points = note_stem_y_points
                        last_note_duration = note_duration


                self.pop_logger_name()
            self.pop_logger_name()
        self.note_canvas.__exit__()

        self.width = dx


    @push_name_to_logger_name_stack_custom("bars")
    def draw_note_bars(self, last_note_stem_y_points, last_note_duration, last_dx,
                       note_stem_y_points, note_duration, dx):  # Fixme: fix flags on bared notes
        self.log_dump(f"Drawing bars with {last_note_stem_y_points} last_note_stem_y_points, {last_note_duration} "
                      f"last_note_duration, {last_dx} last_dx, {note_stem_y_points} note_stem_y_points, {note_duration}"
                      f" note_duration and {dx} dx")

        if note_duration == Fraction(3, 4):
            self.log_dump(f"Note has a duration of {note_duration} so gets a dot")

            dot_pos = (dx + constants.graphics.note_dot_dpos[0],
                       note_stem_y_points[0] + constants.graphics.note_dot_dpos[1])
            Ellipse(pos=dot_pos, size=constants.graphics.note_dot_size)

            note_duration = Fraction(2, 4)



        if last_note_duration == note_duration:  # Use d1
            self.log_dump("Using bars of last_note_duration because last_note_duration == note_duration")

            for bar_index in range(note_duration_to_bar_or_flag_amount(last_note_duration)):
                Line(points=(last_dx + constants.graphics.note_head_width,
                             last_note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap),
                             dx + constants.graphics.note_head_width,
                             note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)),
                     width=constants.graphics.note_stem_width)


        elif last_note_duration < note_duration:  # Use d2, Flags d1
            self.log_dump("Using bars of note_duration and flags from last_note_duration because last_note_duration < "
                          "note_duration")

            bar_amount = note_duration_to_bar_or_flag_amount(note_duration)
            flag_amount = note_duration_to_bar_or_flag_amount(last_note_duration) - bar_amount

            for bar_index in range(bar_amount):
                Line(points=(last_dx + constants.graphics.note_head_width,
                             last_note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap),
                             dx + constants.graphics.note_head_width,
                             note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)),
                     width=constants.graphics.note_stem_width)

            for bar_index in range(flag_amount):
                Line(points=(last_dx + constants.graphics.note_head_width,
                             last_note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap) -
                                constants.graphics.note_flag_gap,
                             dx + constants.graphics.note_head_width - ((dx + constants.graphics.note_head_width -
                                                                         last_dx + constants.graphics.note_head_width)
                                                                        / 2),
                             note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap) -
                                ((note_stem_y_points[1] - last_note_stem_y_points[1]) / 2) -
                                constants.graphics.note_flag_gap),
                     width=constants.graphics.note_stem_width)


        elif last_note_duration > note_duration:  # Use d1, Flags d2
            self.log_dump("Using bars of last_note_duration and flags from note_duration because last_note_duration > "
                          "note_duration")

            bar_amount = note_duration_to_bar_or_flag_amount(last_note_duration)
            flag_amount = note_duration_to_bar_or_flag_amount(note_duration) - bar_amount

            for bar_index in range(bar_amount):
                Line(points=(last_dx + constants.graphics.note_head_width,
                             last_note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap),
                             dx + constants.graphics.note_head_width,
                             note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)),
                     width=constants.graphics.note_stem_width)

            for bar_index in range(flag_amount):
                Line(points=(last_dx + constants.graphics.note_head_width +
                                ((dx + constants.graphics.note_head_width - last_dx +
                                  constants.graphics.note_head_width) / 2),
                             last_note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap) -
                                ((last_note_stem_y_points[1] - note_stem_y_points[1]) / 2) -
                                constants.graphics.note_flag_gap,
                             dx + constants.graphics.note_head_width,
                             note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap) -
                                constants.graphics.note_flag_gap),
                     width=constants.graphics.note_stem_width)




    @push_name_to_logger_name_stack_custom("flags")
    def draw_note_flags(self, note_stem_y_points, note_duration, dx):
        self.log_dump(f"Drawing flags on note with {note_duration} duration and is at ({dx}, {note_stem_y_points})")

        if note_duration == Fraction(3, 4):
            self.log_dump(f"Note has a duration of {note_duration} so gets a dot")

            dot_pos = (dx + constants.graphics.note_dot_dpos[0],
                       note_stem_y_points[0] + constants.graphics.note_dot_dpos[1])
            Ellipse(pos=dot_pos, size=constants.graphics.note_dot_size)

            note_duration = Fraction(2, 4)

        flag_amount = note_duration_to_bar_or_flag_amount(note_duration)
        for flag_index in range(flag_amount):
            Line(points=(dx + constants.graphics.note_head_width,
                            note_stem_y_points[1] - (flag_index * constants.graphics.note_flag_gap),
                         dx + constants.graphics.note_head_width + constants.graphics.note_flag_dpos[0],
                            note_stem_y_points[1] - (flag_index * constants.graphics.note_flag_gap) +
                            constants.graphics.note_flag_dpos[1]),
                 width=constants.graphics.note_stem_width)




    @push_name_to_logger_name_stack_custom("rests")
    def draw_compressed_rests(self, beat_notes, dx):
        sub_beats_to_skip = 0
        _sub_beats_to_skip = 0
        had_not_rest = False

        for note_index, notes in enumerate(beat_notes):
            if _sub_beats_to_skip > 0:
                _sub_beats_to_skip -= 1


            elif not had_not_rest:
                if notes == ["."]:

                    if note_index < 1 and all([beat_notes[note_index + n] == ["."]
                                                                 for n in range(1, 4)]):
                        self.log_dump(f"All sub beats are rests, drawing "
                                      f"{constants.score.duration_to_text_duration[self.notes_per_beat / 4]}_rest")
                        sub_beats_to_skip += 3
                        _sub_beats_to_skip += 3
                        draw_note(f"{constants.score.duration_to_text_duration[self.notes_per_beat / 4]}_rest", dx)

                    elif note_index < len(beat_notes) - 1 and beat_notes[note_index + 1] == ["."]:
                        self.log_dump(f"2 sub beats are rests, drawing "
                                      f"{constants.score.duration_to_text_duration[self.notes_per_beat / 2]}_rest")
                        sub_beats_to_skip += 1
                        _sub_beats_to_skip += 1
                        draw_note(f"{constants.score.duration_to_text_duration[self.notes_per_beat / 2]}_rest", dx)

                    else:
                        self.log_dump(f"1 sub beat is a rests, drawing "
                                      f"{constants.score.duration_to_text_duration[self.notes_per_beat / 1]}_rest")

                        draw_note(f"{constants.score.duration_to_text_duration[self.notes_per_beat]}_rest", dx)

                    dx += constants.graphics.note_width

                else:
                    had_not_rest = True

        self.log_dump(f"{sub_beats_to_skip} sub beats need to be skipped")

        return sub_beats_to_skip, dx


    @reset_logger_name_stack_for_function
    @push_name_to_logger_name_stack
    def get_stem_y_points(self, notes) -> list[tuple[float, float]]:
        music_notes = [_notes for _notes in notes if _notes != ["."]]
        self.log_dump(f"There are {len(music_notes)} notes, looking for special rule")

        # Zero Notes -------------
        if len(music_notes) == 0:
            self.log_dump("No music notes written / only rests, so no need for Bars or Flags")
            return []

        # One Note ---------------
        elif len(music_notes) == 1:
            self.log_dump(f"Special rule for 1 found")
            ret = [(float(min([constants.score.note_name_to_staff_level[note_name] for note_name in music_notes[0]]) *
                    constants.graphics.staff_gap + (constants.graphics.staff_gap / 2)),

                    float(max([constants.score.note_name_to_staff_level[note_name] for note_name in music_notes[0]]) *
                    constants.graphics.staff_gap + (constants.graphics.staff_gap / 2) +
                    constants.graphics.note_stem_height)
                    )]
            self.log_dump(f"Got {ret}")

            return ret

        # Two Notes --------------
        elif len(music_notes) == 2:
            self.log_dump(f"Special rule for 2 found")
            ret = [(float(min([constants.score.note_name_to_staff_level[note_name] for note_name in _notes]) *
                    constants.graphics.staff_gap + (constants.graphics.staff_gap / 2)),

                    float(max([constants.score.note_name_to_staff_level[note_name] for note_name in _notes]) *
                    constants.graphics.staff_gap + (constants.graphics.staff_gap / 2) +
                    constants.graphics.note_stem_height)
                    ) for _notes in music_notes]
            self.log_dump(f"Got {ret}")

            return ret


        # More ----------------------
        else:
            self.log_dump(f"No special rule found")
            ret = [(float(min([constants.score.note_name_to_staff_level[note_name] for note_name in _notes]) *
                          constants.graphics.staff_gap + (constants.graphics.staff_gap / 2)),

                    float(max([constants.score.note_name_to_staff_level[note_name] for note_name in _notes]) *
                          constants.graphics.staff_gap + (constants.graphics.staff_gap / 2) +
                          constants.graphics.note_stem_height)
                    ) for _notes in music_notes]

            highest_y_up = 0
            for y_down, y_up in ret:
                if y_up > highest_y_up:
                    highest_y_up = y_up

            ret = [(y_down, highest_y_up) for y_down, y_up in ret]

            self.log_dump(f"Got {ret}")

            return ret


def draw_note(note_name, x):
    note_shape = note_name

    if note_name in ["kick", "snare"]:
        note_shape = "circle"


    if note_shape in rest_textures.keys():
        Rectangle(pos=(x, 0), size=(constants.graphics.note_width, constants.graphics.staff_height),
                  texture=rest_textures[note_shape])
        return x, 0


    elif note_shape in note_head_textures.keys():
        Rectangle(pos=(x, constants.score.note_name_to_staff_level[note_name] * constants.graphics.staff_gap),
                  size=(constants.graphics.note_head_width, constants.graphics.staff_gap),
                  texture=note_head_textures[note_shape])
        return x, constants.score.note_name_to_staff_level[note_name] * constants.graphics.staff_gap





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


def get_note_duration(notes, note_index, notes_per_beat):
    notes_after_note_index = notes[note_index + 1:len(notes)]

    i = 1
    for note in notes_after_note_index:
        if note != ["."]:
            break

        i += 1

    return Fraction(i, notes_per_beat)


def parse_notes_too_list(string: str) -> list[list[str]]:
    return [[note for note in notes.split(",")] for notes in string.split(" ")]
