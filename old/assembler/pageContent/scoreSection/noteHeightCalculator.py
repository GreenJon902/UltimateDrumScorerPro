import math

from kivy import Logger
from kivy.clock import Clock
from score import Note, ScoreSectionStorage
from score.notes import notes, missing_major_note_level_height


class NoteHeightCalculator:  # Stores an instance of each note at the correct height depending on the given scoreStorage
    note_objects: dict[int, Note]
    update = None
    scoreSectionStorage: ScoreSectionStorage
    _last_used_note_ids = None

    def __init__(self, scoreSectionStorage=None):
        self.scoreSectionStorage = scoreSectionStorage

        self.note_objects = {note_id: note_type() for note_id, note_type in notes.items()}
        self.update = Clock.create_trigger(self.update_, -1)

    def update_(self, _):
        if self.scoreSectionStorage is None:
            Logger.warning(f"NoteHeightCalculator: Tried to update but {self} has no score")
            return

        used_note_ids = {note_id for section in self.scoreSectionStorage for note_id in section.note_ids}  # Ids actually in scoreStorage
        if self._last_used_note_ids == used_note_ids:
            return
        self._last_used_note_ids = used_note_ids

        #  Get note levels as y levels ---------------------------------------------------------------------------------
        note_level_heights = {}  # Height at each note_level
        major_note_levels = set()  # Integer part of note levels
        for note_id in used_note_ids:
            note = self.note_objects[note_id]
            note_level_heights[note.note_level] = note.height
            major_note_levels.add(math.floor(note.note_level))
        if len(note_level_heights) != 0:
            max_note_level = max(note_level_heights.keys())
        else:
            max_note_level = 1
        missing_levels = major_note_levels.symmetric_difference(range(1, math.floor(max_note_level) + 1))
        note_level_heights.update({level: missing_major_note_level_height for level in missing_levels})

        y = 0
        note_level_ys = {}
        for note_level in sorted(note_level_heights.keys(), reverse=True):
            note_level_ys[note_level] = y
            y += note_level_heights[note_level]

        # Set notes to their y levels ----------------------------------------------------------------------------------
        for note in self.note_objects.values():
            if note.note_level in note_level_ys:
                note.top = -note_level_ys[note.note_level]
            else:
                note.y = 0

    def __str__(self):
        contents = (', '.join([
            str(self.note_objects[note_id].y)
            for note_id in
            sorted(self.note_objects.keys())]))

        return f"NoteHeightCalculator<{contents}>"
