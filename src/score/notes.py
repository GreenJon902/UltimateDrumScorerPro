from kivy.factory import Factory
from kivy.lang import Builder, global_idmap
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout

Builder.load_file("score/notes.kv")


# Height is figured out by parent using the drawing_height and note_level(optional).
class Note(RelativeLayout):
    drawing_height: float = NumericProperty()  # The actual height of what is drawn
    stem_connection_offset: float = NumericProperty()  # Offset from relative y=0 where stem connects
    note_level: float = NumericProperty()  # The level upon which the note is drawn, the integer part will always affect
    # the height, the decimal part is only used when there are two notes with the
    # same integer part.
    dot_offset_x: float = NumericProperty()
    dot_offset_y: float = NumericProperty()
    dot_offset: tuple[float, float] = ReferenceListProperty(dot_offset_x, dot_offset_y)
    name: str = StringProperty()

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)


notes: dict[float, type[Note]] = {}
for (id, note_name) in global_idmap["notes"].items():
    notes[id] = Factory.get(note_name)
missing_major_note_level_height = global_idmap["missing_major_note_level_height"]  # If gap in consecutive integer
# note_level values then this is the
# gap
bar_height = global_idmap["bar_height"]
bar_width = global_idmap["st"]
stem_width = global_idmap["st"]
flag_width = global_idmap["st"]
flag_length = global_idmap["flag_length"]
slanted_flag_length = global_idmap["slanted_flag_length"]
slanted_flag_height_offset = global_idmap["slanted_flag_height_offset"]
dot_radius = global_idmap["dot_radius"]
dot_spacing = global_idmap["dot_spacing"]
