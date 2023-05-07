import os

from kivy import Logger
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty

from kv import check_kv
from scoreSectionDesigns import Design, read_design_from

check_kv()


class Note(Design):
    stem_connection_offset: float = NumericProperty()  # Offset from relative y=0 where stem connects
    note_level: float = NumericProperty()  # The level upon which the note is drawn, the integer part will always affect
    # the height, the decimal part is only used when there are two notes with the
    # same integer part.
    dot_offset_x: float = NumericProperty()
    dot_offset_y: float = NumericProperty()

    dot_offset: tuple[float, float] = ReferenceListProperty(dot_offset_x, dot_offset_y)
    name: str = StringProperty()



notes_loaded = False
notes: dict[int, Note] = {}


def check_notes():
    global notes_loaded

    if not notes_loaded:
        Logger.info("[UDSP] Loading note files...")
        for note_path in os.listdir("designs/notes"):
            nid, note = read_design_from(os.path.join("designs/notes", note_path), Note)
            if nid in notes:
                Logger.warning(f"[Notes] Already has note for id {nid}, {notes[nid]} {note}")
            notes[nid] = note
        notes_loaded = True


__all__ = ["Note", "check_notes", "notes"]
