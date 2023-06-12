from math import floor

from renderer.scoreSection.scoreSection_noteHeightCalculatorBase import ScoreSection_NoteHeightCalculatorBase
from scoreSectionDesigns.notes import notes, note_ids_at_level


class ScoreSection_NormalNoteHeightCalculator(ScoreSection_NoteHeightCalculatorBase):
    def get(self, existent_notes_ids):
        existent_notes_ids = sorted(existent_notes_ids, key=lambda nid: notes[nid].note_level)
        highest_major_level = max(floor(notes[nid].note_level) for nid in notes.keys())
        existent_note_levels = {notes[nid].note_level for nid in existent_notes_ids}

        note_levels = set(range(floor(min(existent_note_levels)), highest_major_level + 1))
        note_levels.update(existent_note_levels)
        note_levels = sorted(list(note_levels))

        note_heights = []
        y = 0
        for note_level in note_levels:
            for nid in note_ids_at_level[note_level]:
                note_heights.append([note_level, y])
                y += notes[nid].height
        return note_heights


__all__ = ["ScoreSection_NormalNoteHeightCalculator"]
