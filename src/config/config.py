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

    note_color = (0, 0, 0, 1)

    default_beat_section_count = 8
    section_x_buffer = metrics.cm(0.25)  # At least 2x the width of a note incase there is 2 on the same line
    section_bottom_buffer = metrics.cm(1)
    section_top_buffer = metrics.cm(0)
    focus_speed = 0.25
    note_commit_speed = 0.1
    note_hover_color_fade_speed = 0.1
    section_kill_speed = 0.25
    section_kill_rise_amount = metrics.cm(5)

    section_trash_can_size = metrics.cm(0.5), metrics.cm(0.5)
    section_trash_can_transparency = 0.5
    section_trash_can_hover_fade_speed = 0.1



__all__ = ["Config"]
