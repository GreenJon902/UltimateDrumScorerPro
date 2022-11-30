from kivy import metrics
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty, ColorProperty


class NoteInfo(EventDispatcher):
    y = NumericProperty()

    width = NumericProperty()
    height = NumericProperty()
    size = ReferenceListProperty(width, height)

    color = ColorProperty()
    thickness = NumericProperty()

    symbol: str = StringProperty()


class Config:
    note_info: list[NoteInfo] = [
        NoteInfo(y="2.9cm", size=("0.5cm", "0.5cm"), symbol="8_cross"),  # Crash 1
        NoteInfo(y="2.4cm", size=("0.5cm", "0.5cm"), symbol="cross"),  # Hi-Hat
        NoteInfo(y="2.4cm", size=("0.5cm", "0.5cm"), symbol="8_cross"),  # Crash 2
        NoteInfo(y="2.4cm", size=("0.5cm", "0.5cm"), symbol="circled_cross"),  # Trash
        NoteInfo(y="2.4cm", size=("0.5cm", "0.5cm"), symbol="rotated_square"),  # Ride
        NoteInfo(y="2.4cm", size=("0.5cm", "0.5cm"), symbol="hollow_rotated_square"),  # Ride Bell
        NoteInfo(y="1.8cm", size=("0.5cm", "0.4cm"), symbol="oval_with_tilted_line"),  # Tom 1
        NoteInfo(y="1.5cm", size=("0.5cm", "0.5cm"), symbol="tilted_line_with_arc"),  # Flam Snare
        NoteInfo(y="1.5cm", size=("0.5cm", "0.5cm"), symbol="tilted_line"),  # Snare
        NoteInfo(y="0.9cm", size=("0.5cm", "0.4cm"), symbol="oval_with_tilted_line"),  # Tom 2
        NoteInfo(y="0.5cm", size=("0.5cm", "0.4cm"), symbol="oval_with_tilted_line"),  # Tom 3
        NoteInfo(y="0cm", size=("0.5cm", "0.5cm"), symbol="tilted_line"),  # Kick
        NoteInfo(y="0cm", size=("0.5cm", "0.5cm"), symbol="cross"),  # Hit-Hat Kick
        NoteInfo(y="0cm", size=("0.5cm", "0.5cm"), symbol="circled_cross"),  # Hit-Hat Splash
    ]
    currentNotePain = 0

    line_thickness: int = metrics.cm(0.05)
    note_selector_uncommitted_transparency = 0.3
    note_selector_uncommitted_hover_color = (0, 0, 1)
    note_selector_committed_hover_color = (1, 0.5, 0.5)
    note_selector_distance = metrics.cm(0.5)
    note_selector_x_space = metrics.cm(0.1)

    default_beat_section_count = 4
    default_beat_bars = []
    section_x_buffer = metrics.cm(0.25)  # At least 2x the width of a note incase there is 2 on the same line
    focus_speed = 0.25
    note_commit_speed = 0.1
    note_hover_color_fade_speed = 0.1
    section_kill_speed = 5
    section_kill_rise_amount = metrics.cm(5)
    section_entrance_animation_duration = 0.25
    # FIXME: Issue where when spawning in the first time it jumps (set section_entrance_animation_duration to 5 to see)

    section_trash_can_size = metrics.cm(0.5), metrics.cm(0.5)
    section_trash_can_transparency = 0.5
    section_trash_can_hover_fade_speed = 0.1

    section_extender_height = metrics.cm(0.5)  # width is everything not taken up by the trash can
    section_extender_space = section_extender_height + metrics.cm(0.5)
    section_extender_transparency = 0.3
    section_extender_hover_transparency = 0.7
    section_extender_hover_fade_speed = 0.1

    section_extender_trash_can_buffer = metrics.cm(0.1)

    new_section_button_x_buffer = metrics.cm(0.2)
    new_section_button_size = metrics.cm(0.5), metrics.cm(3)
    new_section_button_transparency = 0.7
    new_section_button_hover_fade_speed = 0.1

    bar_spacing = metrics.cm(0.3)
    bar_side_width = metrics.cm(0.5)
    bar_selector_uncommitted_transparency = 0.3
    bar_selector_uncommitted_hover_color = (0, 0, 1)
    bar_selector_committed_hover_color = (1, 0.5, 0.5)
    bar_selector_hover_fade_speed = 0.25
    bar_split_amount = metrics.cm(0.1)
    bar_split_speed = 0.25
    bar_kill_speed = 0.25
    bar_entrance_speed = 0.1
    bar_top_buffer = metrics.cm(0.5)
    dot_x_buffer = metrics.cm(0.25)  # Spacing at start
    dot_x_spacing = metrics.cm(0.25)
    dot_selector_uncommitted_transparency = 0.3
    dot_radius = metrics.cm(0.05)
    dot_selector_hover_radius = metrics.cm(0.1)
    dot_selector_uncommitted_hover_color = (0, 0, 1)
    dot_selector_committed_hover_color = (1, 0.5, 0.5)
    dot_selector_hover_fade_speed = 0.1
    dot_entrance_speed = 0.25
    dot_kill_speed = 0.25
    default_beat_dot_count = 0
    bar_dot_height = metrics.cm(0.25)



__all__ = ["Config"]
