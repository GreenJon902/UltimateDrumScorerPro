from renderer.scoreSection.scoreSection_noteHeightCalculatorBase import ScoreSection_NoteHeightCalculatorBase
from scoreSectionDesigns.notes import notes, note_ids_at_level


class ScoreSection_NormalNoteHeightCalculator(ScoreSection_NoteHeightCalculatorBase):
    def get(self, existent_notes_ids):
        if len(existent_notes_ids) == 0:
            return [], 0

        # Knowing the note levels, we need to get any extra majors that are above, e.g. [1.1] -> [1.1, 2, 3],
        # [1.1, 2.3] -> [1.1, 2.3, 3], [2] -> [2, 3]

        existent_levels = {notes[nid].note_level for nid in existent_notes_ids}
        existent_major_levels = {int(level) for level in existent_levels}
        lowest_existent_major_level = min(existent_major_levels)
        highest_major_level = max(int(notes[nid].note_level) for nid in notes)

        major_levels = set(range(lowest_existent_major_level,
                                 highest_major_level + 1))
        missing_major_levels = major_levels.symmetric_difference(existent_major_levels)

        note_levels = existent_levels
        note_levels.update(missing_major_levels)
        note_levels = sorted(list(note_levels))  # Use set before so no duplicates, but we now want it ordered

        note_heights = []
        y = 0
        for note_level in note_levels:
            for nid in note_ids_at_level[note_level]:
                note_heights.append([note_level, y])
                y += notes[nid].height
        return note_heights, y


__all__ = ["ScoreSection_NormalNoteHeightCalculator"]
