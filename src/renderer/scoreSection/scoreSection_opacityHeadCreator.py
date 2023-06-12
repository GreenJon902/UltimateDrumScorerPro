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

    def create(self, present_note_ids, note_heights):
        group = InstructionGroup()
        info = self.update(present_note_ids, note_heights, group)
        return info


    def update(self, present_note_ids, note_heights, group):
        group.clear()
        group.add(PushMatrix())

        lowest_info = None

        width = 0
        height = 0
        y = 0
        for (note_level, note_height) in note_heights:
            for nid in note_ids_at_level[note_level]:
                if nid in present_note_ids and lowest_info is None:
                    lowest_info = height, nid

                color = self.present_color if nid in present_note_ids else self.absent_color
                if color[3] != 0:  # If we actually need to draw it
                    group.add(Color(rgba=color))
                    group.add(notes[nid].make_canvas(color=False))
                group.add(Translate(0, y))
                y = note_height - y

                if notes[nid].width > width and nid in present_note_ids:
                    width = notes[nid].width
                height += notes[nid].height

        group.add(PopMatrix())
        return group, width, height, lowest_info


__all__ = ["ScoreSection_OpacityHeadCreator"]
