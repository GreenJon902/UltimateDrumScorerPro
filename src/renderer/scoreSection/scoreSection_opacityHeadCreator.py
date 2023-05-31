from math import floor

from kivy.graphics import Color, InstructionGroup, Translate, PushMatrix, PopMatrix

from renderer.scoreSection.scoreSection_headCreatorBase import ScoreSection_HeadCreatorBase
from scoreSectionDesigns.notes import notes, check_notes, note_ids_at_level

check_notes()


class ScoreSection_OpacityHeadCreator(ScoreSection_HeadCreatorBase):  # TODO: update this to the new note level system
    present_color: tuple[float, float, float, float]
    absent_color: tuple[float, float, float, float]

    def __init__(self, present_color, absent_color):
        self.present_color = present_color
        self.absent_color = absent_color

    def create(self, present_note_ids, existent_notes_ids):
        group = InstructionGroup()
        group.add(PushMatrix())

        existent_notes_ids = sorted(existent_notes_ids, key=lambda nid: notes[nid].note_level)
        highest_major_level = max(floor(notes[nid].note_level) for nid in notes.keys())
        existent_note_levels = {notes[nid].note_level for nid in existent_notes_ids}

        note_levels = set(range(floor(min(existent_note_levels)), highest_major_level + 1))
        note_levels.update(existent_note_levels)
        note_levels = sorted(list(note_levels))

        lowest_info = None

        width = 0
        height = 0
        for note_level in note_levels:
            for nid in note_ids_at_level[note_level]:
                if nid in present_note_ids:
                    lowest_info = height, nid

                color = self.present_color if nid in present_note_ids else self.absent_color
                if color[3] != 0:  # If we actually need to draw it
                    group.add(Color(rgba=color))
                    group.add(notes[nid].make_canvas(color=False))
                group.add(Translate(0, notes[nid].height))

                if notes[nid].width > width:
                    width = notes[nid].width
                height += notes[nid].height

        group.add(PopMatrix())
        return group, width, height, lowest_info




__all__ = ["ScoreSection_OpacityHeadCreator"]
