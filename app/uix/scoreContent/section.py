from fractions import Fraction
from math import log
from typing import Optional

from kivy.animation import Animation, AnimationTransition
from kivy.atlas import Atlas
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Canvas, Color
from kivy.input import MotionEvent
from kivy.properties import NumericProperty, OptionProperty, ListProperty, ReferenceListProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout

import constants
from app.globalBindings import GlobalBindings
from app.mathVertexInstructions import MathLine, MathEllipse, MathRectangle
from app.misc import check_mode
from app.popups.addSectionPopup import AddSectionPopup
from app.uix.scoreContent.scoreContentWithPopup import ScoreContentWithPopup
from logger import push_name_to_logger_name_stack, ClassWithLogger, reset_logger_name_stack_for_function, \
    push_name_to_logger_name_stack_custom

rest_textures = Atlas("resources/atlases/rests.atlas").textures
note_head_textures = Atlas("resources/atlases/note_heads.atlas").textures

none_music_note_expand_transition = getattr(AnimationTransition, constants.graphics.none_music_note_expand_transition)


class Section(ScoreContentWithPopup, ClassWithLogger):
    notes: list = ListProperty()
    notes_per_beat = NumericProperty()
    title: str = StringProperty()

    time_signature_a: list = NumericProperty()
    time_signature_b: list = NumericProperty()
    time_signature: list = ReferenceListProperty(time_signature_a, time_signature_b)

    content: RelativeLayout

    required_mode = "section"

    update = None
    mode = None
    
    def __init__(self, **kwargs):
        ClassWithLogger.__init__(self)
        ScoreContentWithPopup.__init__(self, **kwargs)

        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())
        Window.bind(mouse_pos=self.on_mouse_move)
        GlobalBindings.bind(mode=self.change_mode)

        self.time_signature, self.notes_per_beat, self.notes = self.parse_string("4/4-4[. . . . . . . . . . . . . . . ."
                                                                                 "]")


    def on_kv_post(self, base_widget):
        self.content = self.ids["content"]

    def on_title(self, _instance, value):
        self.ids["title_text"].text = value

    def get_popup_class(self, **kwargs):
        return AddSectionPopup(**kwargs)

    def popup_submitted(self, instance, data):
        self.title = data.pop("title", "No Title Given")

        self.update()

    def open_popup_with_pre_values(self):
        self.popup(title=self.title)


    def parse_string(self, string):
        parts = string.split("-")

        ts = parts[0].split("/")
        time_signature = int(ts[0]), int(ts[1])
        notes_per_beat = int(parts[1].split("[")[0])
        notes = [note.split(",") for note in parts[1].split("[")[1].replace("]", "").split(" ")]

        notes = [([] if note == ["."] else note) for note in notes]

        self.log_debug(f"Parsed {string} too ts={time_signature} npb={notes_per_beat} notes={notes}")
        return time_signature, notes_per_beat, notes


    def change_mode(self, mode):
        self.mode = mode

    def on_mouse_move(self, _instance, pos):
        if self.mode == "note":
            pos = self.to_widget(*pos)

            child: Bar
            for child in self.content.children:
                animation: Optional[Animation]

                if child.current_animation_info is not None:
                    animation, direction = child.current_animation_info

                else:
                    animation, direction = None, None


                if child.collide_point(*pos):
                    if direction == "in":
                        animation.stop(child)

                        child.current_animation_info = (None, None)
                        animation, direction = None, None



                    if direction is None:
                        animation = Animation(none_music_note_width=constants.graphics.expanded_none_music_note_width,
                                              duration=constants.graphics.none_music_note_expand_time,
                                              transition=none_music_note_expand_transition)
                        animation.start(child)
                        child.current_animation_info = (animation, "out")


                    # Future note place
                    r_pos = child.to_local(*pos)
                    note_index, staff_level = child.pos_to_note(*r_pos)

                    if note_index is not None:
                        note_type = constants.score.staff_level_to_note_name[
                            min(constants.score.staff_level_to_note_name.keys(), key=lambda x: abs(staff_level - x))]

                        child.temp_note_index = note_index
                        child.temp_note_type = note_type



                else:
                    if direction == "out":
                        animation.stop(child)

                        child.current_animation_info = (None, None)
                        animation, direction = None, None

                    if direction is None:
                        animation = Animation(none_music_note_width=constants.graphics.default_none_music_note_width,
                                              duration=constants.graphics.none_music_note_expand_time,
                                              transition=none_music_note_expand_transition)
                        animation.start(child)
                        child.current_animation_info = (animation, "in")

                    child.temp_note_index = None
                    child.temp_note_type = None


    @push_name_to_logger_name_stack
    def _update(self):
        beats_per_bar = self.notes_per_beat * self.time_signature[0]
        self.log_debug(f"{beats_per_bar} beats per bar")
        bars_needed = len(self.notes) / beats_per_bar

        # if bars_needed is 1.0 or 2.0 then int(bars_needed) == 1 or 2 which still == bars_needed,
        # but if it is 1.5 then it doesnt == int(bars_needed) which is 2
        assert bars_needed == int(bars_needed)

        bars_needed = int(bars_needed)
        bars_too_add = bars_needed - len(self.content.children)
        self.log_debug(f"Adding {bars_too_add} bar widgets too self from {bars_needed} out of "
                       f"{len(self.content.children)}")


        for _ in range(bars_too_add):
            b = Bar()
            b.bind(width=self.do_width)
            self.content.add_widget(b)

        for n, child in enumerate(self.content.children):
            notes = self.notes[n * beats_per_bar:(n + 1) * beats_per_bar]

            child.notes_per_beat = self.notes_per_beat
            child.notes = notes
            self.log_dump(f"Giving {child} \"{notes}\"")

        self.content.children[0].bar_start_line_type = "repeat"
        self.content.children[-1].bar_end_line_type = "repeat"


    def do_width(self, _instance, _value):
        width = 0
        for child in self.content.children:
            child.x = width
            width += child.width
        self.width = width


    def on_touch_up(self, touch: MotionEvent):
        if check_mode("note") and self.collide_point(*touch.pos):
            pos = self.to_local(*touch.pos)

            child: Bar
            for child in self.content.children:
                r_pos = child.to_local(*pos)
                note_index, staff_level = child.pos_to_note(*r_pos)

                if note_index is not None:
                    note_type = constants.score.staff_level_to_note_name[
                        min(constants.score.staff_level_to_note_name.keys(), key=lambda x: abs(staff_level - x))]

                    if note_type in self.notes[note_index]:
                        self.log_debug(f"Removing note of level {staff_level} which is {note_type} at {note_index}")

                        self.notes[note_index].remove(note_type)
                        child.update()

                    else:
                        self.log_debug(f"Added note of level {staff_level} which is {note_type} at {note_index}")

                        self.notes[note_index].append(note_type)
                        child.update()
                    self.update()

                    return True


        else:
            return ScoreContentWithPopup.on_touch_up(self, touch)



class Bar(RelativeLayout, ClassWithLogger):
    update: callable
    current_animation_info: tuple[Animation, str] = None
    """
    Used by :class:`Section` for expanding the bar when the mouse is over it
    """

    notes: list = ListProperty()
    notes_per_beat: int = NumericProperty()
    none_music_note_width = NumericProperty(constants.graphics.default_none_music_note_width)

    temp_note_index = NumericProperty(None, allownone=True)
    temp_note_type = StringProperty(None, allownone=True)

    _current_not_drawn_rests: int = NumericProperty()
    _current_dx: int = NumericProperty()

    bar_start_line_type: str = OptionProperty("single", options=["single", "repeat"])
    bar_end_line_type: str = OptionProperty("single", options=["single", "repeat"])

    _bar_start_line_width: int = NumericProperty(constants.graphics.bar_edge_line_width)
    _bar_end_line_width: int = NumericProperty(constants.graphics.bar_edge_line_width)

    note_canvas: Canvas

    def __init__(self, **kwargs):
        ClassWithLogger.__init__(self)

        self.note_canvas = Canvas()
        self.update = Clock.create_trigger(lambda _elapsed_time: self._update())
        self.do_width = Clock.create_trigger(lambda _elapsed_time: self._do_width())
        self.bind(notes=lambda _instance, _value: self.update(), notes_per_beat=lambda _instance, _value: self.update(),
                  none_music_note_width=lambda _instance, _value: self.do_width(),
                  temp_note_index=lambda _instance, _value: self.update(),
                  temp_note_type=lambda _instance, _value: self.update(),
                  _current_not_drawn_rests=lambda _instance, _value: self.do_width(),
                  _current_dx=lambda _instance, _value: self.do_width())

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


    def _do_width(self):
        self.width = self._current_dx + (self._current_not_drawn_rests * self.none_music_note_width)


    def pos_to_note(self, x, y):
        dx = (constants.graphics.note_head_width * -1) + constants.graphics.bar_start_padding

        for note_index, notes in enumerate(self.notes):
            if not notes:
                dx += self.none_music_note_width

            else:
                dx += constants.graphics.note_width

            if x < dx:
                return note_index, ((y - (constants.graphics.staff_gap / 2)) / constants.graphics.staff_gap)

        return None, None




    @push_name_to_logger_name_stack
    def _update(self):
        notes_per_beat = self.notes_per_beat

        _all_notes = self.notes.copy()
        if self.temp_note_index is not None:
            _all_notes[self.temp_note_index] = ((_all_notes[self.temp_note_index] + [self.temp_note_type]) if
                                                 _all_notes[self.temp_note_index] != [] else [self.temp_note_type])
        all_notes = [_all_notes[n:n + 4] for n in range(0, len(_all_notes), notes_per_beat)]
        self.log_debug(f"Got notes_per_beat: {notes_per_beat}, all_notes: {all_notes}")
        self.log_dump()

        dx = 0
        not_drawn_rests_this_bar = 0
        last_not_drawn_rests_this_bar = 0
        total_note_index = 0


        self.note_canvas.clear()
        self.note_canvas.__enter__()
        Color(rgb=constants.graphics.note_color)

        dx += constants.graphics.bar_start_padding
        for beat_index, beat_notes in enumerate(all_notes):
            self.log_dump()
            self.log_debug(f"Beat {beat_index + 1} --------------| notes: {beat_notes} |--------------")
            self.push_logger_name(f"beat_{beat_index}")

            sub_beats_to_skip, dx, did_draw_rest = self.draw_compressed_rests(beat_notes, dx, not_drawn_rests_this_bar)
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
                    if sub_beats_to_skip != 0:
                        not_drawn_rests_this_bar += 1

                    sub_beats_to_skip -= 1

                else:
                    if not notes:
                        if not did_draw_rest:
                            not_drawn_rests_this_bar += 1

                    else:
                        did_draw_rest = False
                        note_stem_y_points = stem_y_points[music_notes_draw_this_beat]

                        for note in notes:
                            tmp_note = ((total_note_index == self.temp_note_index) and (note == self.temp_note_type))
                            print(tmp_note, (total_note_index == self.temp_note_index), (note == self.temp_note_type), total_note_index, self.temp_note_index)
                            if tmp_note:
                                if self.temp_note_type in self.notes[self.temp_note_index]:
                                    Color(rgb=constants.graphics.temp_note_that_exists_color)

                                else:
                                    Color(rgb=constants.graphics.temp_note_color)

                            draw_note(self, note, dx, not_drawn_rests_this_bar)

                            if tmp_note:
                                Color(rgb=constants.graphics.note_color)

                            MathLine(self, ["none_music_note_width"],
                                     [f"{dx + constants.graphics.note_head_width} + ({not_drawn_rests_this_bar} * "
                                      f"self.none_music_note_width)",
                                      f"{note_stem_y_points[0]}",
                                      f"{dx + constants.graphics.note_head_width} + ({not_drawn_rests_this_bar} * "
                                      f"self.none_music_note_width)",
                                      f"{note_stem_y_points[1]}"],
                                     width=constants.graphics.note_stem_width)




                        if music_notes_draw_this_beat == 0 and all([sub_beat_notes == []  # Flags required
                                                                    for sub_beat_notes in
                                                                    beat_notes[note_index + 1:len(beat_notes)
                                                                               ]]):
                            self.draw_note_flags(note_stem_y_points, note_duration, dx, not_drawn_rests_this_bar)

                        else:  # Bars required
                            if last_note_stem_y_points is not None:
                                self.draw_note_bars(last_note_stem_y_points, last_note_duration, last_note_dx,
                                                    note_stem_y_points, note_duration, dx, not_drawn_rests_this_bar,
                                                    last_not_drawn_rests_this_bar)


                        last_note_dx = dx
                        dx += constants.graphics.note_width
                        music_notes_draw_this_beat += 1

                        last_note_stem_y_points = note_stem_y_points
                        last_note_duration = note_duration

                        last_not_drawn_rests_this_bar = not_drawn_rests_this_bar
                total_note_index += 1


                self.pop_logger_name()
            self.pop_logger_name()
        self.note_canvas.__exit__()

        self._current_not_drawn_rests = not_drawn_rests_this_bar
        self._current_dx = dx


    @push_name_to_logger_name_stack_custom("bars")
    def draw_note_bars(self, last_note_stem_y_points, last_note_duration, last_dx,
                       note_stem_y_points, note_duration, dx, not_drawn_rests_this_beat,
                       last_not_drawn_rests_this_beat):
        self.log_dump(f"Drawing bars with {last_note_stem_y_points} last_note_stem_y_points, {last_note_duration} "
                      f"last_note_duration, {last_dx} last_dx, {note_stem_y_points} note_stem_y_points, {note_duration}"
                      f" note_duration, {dx} dx, {not_drawn_rests_this_beat}, none_draw_rests_this_beat, "
                      f"{last_not_drawn_rests_this_beat}")

        if note_duration == Fraction(3, 4):
            self.log_dump(f"Note has a duration of {note_duration} so gets a dot")

            MathEllipse(self, ["none_music_note_width"],
                        (f"{dx + constants.graphics.note_dot_dpos[0]} + ({not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                           f"{note_stem_y_points[0] + constants.graphics.note_dot_dpos[1]}"),
                        size=constants.graphics.note_dot_size)

            note_duration = Fraction(2, 4)



        if last_note_duration == note_duration:  # Use d1
            self.log_dump("Using bars of last_note_duration because last_note_duration == note_duration")

            for bar_index in range(note_duration_to_bar_or_flag_amount(last_note_duration)):
                MathLine(self, ["none_music_note_width"],
                         [f"{last_dx + constants.graphics.note_head_width} + ({last_not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                            f"{last_note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)}",
                            f"{dx + constants.graphics.note_head_width} + ({not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                            f"{note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)}"],
                         width=constants.graphics.note_stem_width)


        elif last_note_duration < note_duration:  # Use d2, Flags d1
            self.log_dump("Using bars of note_duration and flags from last_note_duration because last_note_duration < "
                          "note_duration")

            bar_amount = note_duration_to_bar_or_flag_amount(note_duration)
            flag_amount = note_duration_to_bar_or_flag_amount(last_note_duration) - bar_amount

            for bar_index in range(bar_amount):
                MathLine(self, ["none_music_note_width"],
                         [f"{last_dx + constants.graphics.note_head_width} + ({last_not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                            f"{last_note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)}",
                            f"{dx + constants.graphics.note_head_width} + ({not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                            f"{note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)}"],
                         width=constants.graphics.note_stem_width
                         )

            for flag_index in range(flag_amount):
                MathLine(self, ["none_music_note_width"],
                         [f"{last_dx + constants.graphics.note_head_width} + ({not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                            f"""{last_note_stem_y_points[1] - (flag_index * constants.graphics.note_flag_gap) - 
                                 constants.graphics.note_flag_gap}""",
                            f"""({dx + constants.graphics.note_head_width - ((dx - last_dx) / 2)} + 
                                ({not_drawn_rests_this_beat} * self.none_music_note_width))""",
                            f"""{note_stem_y_points[1] - (flag_index * constants.graphics.note_flag_gap) -
                                 ((note_stem_y_points[1] - last_note_stem_y_points[1]) / 2) -
                                 constants.graphics.note_flag_gap}"""],
                         width=constants.graphics.note_stem_width)


        elif last_note_duration > note_duration:  # Use d1, Flags d2
            self.log_dump("Using bars of last_note_duration and flags from note_duration because last_note_duration > "
                          "note_duration")

            bar_amount = note_duration_to_bar_or_flag_amount(last_note_duration)
            flag_amount = note_duration_to_bar_or_flag_amount(note_duration) - bar_amount

            for bar_index in range(bar_amount):
                MathLine(self, ["none_music_note_width"],
                         [f"{last_dx + constants.graphics.note_head_width} + ({last_not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                            f"{last_note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)}",
                            f"{dx + constants.graphics.note_head_width} + ({not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                            f"{note_stem_y_points[1] - (bar_index * constants.graphics.note_flag_gap)}"],
                         width=constants.graphics.note_stem_width)


            for flag_index in range(flag_amount):
                MathLine(self, ["none_music_note_width"],
                         [f"""{last_dx + constants.graphics.note_head_width +
                               ((dx - last_dx) / 2)} + ({not_drawn_rests_this_beat} * 
                                self.none_music_note_width)""",
                            f"""{last_note_stem_y_points[1] - (flag_index * constants.graphics.note_flag_gap) -
                                 ((last_note_stem_y_points[1] - note_stem_y_points[1]) / 2) -
                                 constants.graphics.note_flag_gap}""",
                            f"{dx + constants.graphics.note_head_width} + ({not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                            f"""{note_stem_y_points[1] - (flag_index * constants.graphics.note_flag_gap) -
                                 constants.graphics.note_flag_gap}"""],
                         width=constants.graphics.note_stem_width)




    @push_name_to_logger_name_stack_custom("flags")
    def draw_note_flags(self, note_stem_y_points, note_duration, dx, not_drawn_rests_this_beat):
        self.log_dump(f"Drawing flags on note with {note_duration} duration and is at ({dx}, {note_stem_y_points})")

        if note_duration == Fraction(3, 4):
            self.log_dump(f"Note has a duration of {note_duration} so gets a dot")

            MathEllipse(self, ["none_music_note_width"],
                        (f"{dx + constants.graphics.note_dot_dpos[0]} + ({not_drawn_rests_this_beat} * "
                           f"self.none_music_note_width)",
                           f"{note_stem_y_points[0] + constants.graphics.note_dot_dpos[1]}"),
                        size=constants.graphics.note_dot_size)

            note_duration = Fraction(2, 4)

        flag_amount = note_duration_to_bar_or_flag_amount(note_duration)
        for flag_index in range(flag_amount):
            MathLine(self, ["none_music_note_width"],
                     [f"{dx + constants.graphics.note_head_width} + ({not_drawn_rests_this_beat} * "
                                f"self.none_music_note_width)",
                        f"{note_stem_y_points[1] - (flag_index * constants.graphics.note_flag_gap)}",
                        f"""{dx + constants.graphics.note_head_width + constants.graphics.note_flag_dpos[0]} + \
                            ({not_drawn_rests_this_beat} * self.none_music_note_width)""",
                        f"""{note_stem_y_points[1] - (flag_index * constants.graphics.note_flag_gap) + 
                             constants.graphics.note_flag_dpos[1]}"""],
                     width=constants.graphics.note_stem_width)




    @push_name_to_logger_name_stack_custom("rests")
    def draw_compressed_rests(self, beat_notes, dx, not_drawn_rests_this_beat):
        sub_beats_to_skip = 0
        _sub_beats_to_skip = 0
        had_not_rest = False
        did_draw_rest = False

        for note_index, notes in enumerate(beat_notes):
            if _sub_beats_to_skip > 0:
                _sub_beats_to_skip -= 1


            elif not had_not_rest:
                if not notes:

                    if note_index < 1 and all([beat_notes[note_index + n] == []
                                                                 for n in range(1, 4)]):
                        self.log_dump(f"All sub beats are rests, drawing "
                                      f"{constants.score.duration_to_text_duration[self.notes_per_beat / 4]}_rest")
                        sub_beats_to_skip += 3
                        _sub_beats_to_skip += 3
                        draw_note(self, f"{constants.score.duration_to_text_duration[self.notes_per_beat / 4]}_rest",
                                  dx, not_drawn_rests_this_beat)

                    elif note_index < len(beat_notes) - 1 and beat_notes[note_index + 1] == []:
                        self.log_dump(f"2 sub beats are rests, drawing "
                                      f"{constants.score.duration_to_text_duration[self.notes_per_beat / 2]}_rest")
                        sub_beats_to_skip += 1
                        _sub_beats_to_skip += 1
                        draw_note(self, f"{constants.score.duration_to_text_duration[self.notes_per_beat / 2]}_rest",
                                  dx, not_drawn_rests_this_beat)

                    else:
                        self.log_dump(f"1 sub beat is a rests, drawing "
                                      f"{constants.score.duration_to_text_duration[self.notes_per_beat / 1]}_rest")

                        draw_note(self, f"{constants.score.duration_to_text_duration[self.notes_per_beat]}_rest", dx,
                                  not_drawn_rests_this_beat)

                    dx += constants.graphics.note_width
                    did_draw_rest = True

                else:
                    had_not_rest = True

        self.log_dump(f"{sub_beats_to_skip} sub beats need to be skipped")

        return sub_beats_to_skip, dx, did_draw_rest


    @reset_logger_name_stack_for_function
    @push_name_to_logger_name_stack
    def get_stem_y_points(self, notes) -> list[tuple[float, float]]:
        music_notes = [_notes for _notes in notes if _notes != []]
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


def draw_note(instance, note_name, x, not_drawn_rests_this_beat):
    note_shape = note_name

    if note_name in ["kick", "snare", "floor_tom", "middle_tom", "high_tom"]:
        note_shape = "circle"


    if note_shape in rest_textures.keys():
        MathRectangle(instance, ["none_music_note_width"],
                      [f"{x} + ({not_drawn_rests_this_beat} * self.none_music_note_width)",
                         f"0"],
                      size=(constants.graphics.note_width, constants.graphics.staff_height),
                      texture=rest_textures[note_shape])
        return x, 0


    elif note_shape in note_head_textures.keys():
        MathRectangle(instance, ["none_music_note_width"],
                      [f"{x} + ({not_drawn_rests_this_beat} * self.none_music_note_width)",
                         f"{constants.score.note_name_to_staff_level[note_name] * constants.graphics.staff_gap}"],
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
        if note:
            break

        i += 1

    return Fraction(i, notes_per_beat)


def parse_notes_too_list(string: str) -> list[list[str]]:
    return [[note for note in notes.split(",")] for notes in string.split(" ")]
