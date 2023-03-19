from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder, global_idmap
from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout

Builder.load_file("score/notes.kv")


# Height is figured out by parent using the drawing_height and note_level(optional).
class Note(RelativeLayout):
    drawing_height: float = NumericProperty()  # The actual height of what is drawn
    note_level: float = NumericProperty()  # The level upon which the note is drawn, the integer part will always affect
                                           # the height, the decimal part is only used when there are two notes with the
                                           # same integer part.

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)


notes = {}
for (id, note_name) in global_idmap["notes"].items():
    notes[id] = Factory.get(note_name)
missing_major_note_level_height = global_idmap["missing_major_note_level_height"]  # If gap in consecutive integer
                                                                                   # note_level values then this is the
                                                                                   # gap
