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

    def create(self, group, note_level_info, nids):
        if group is None:
            group = InstructionGroup()

        group.clear()
        group.add(PushMatrix())

        width = 0
        y = 0
        stem_connection_point = None
        for (note_level, note_height) in note_level_info:
            for nid in note_ids_at_level[note_level]:
                if nid in nids and (stem_connection_point is None or
                                    (note_height + notes[nid].stem_connection_offset) > stem_connection_point):
                    stem_connection_point = (note_height + notes[nid].stem_connection_offset)

                y = note_height - y
                group.add(Translate(0, y))

                color = self.present_color if nid in nids else self.absent_color
                if color[3] != 0:  # If we actually need to draw it
                    group.add(Color(rgba=color))
                    group.add(notes[nid].make_canvas(color=False))

                if notes[nid].width > width and nid in nids:
                    width = notes[nid].width

        group.add(PopMatrix())

        return group, width, stem_connection_point



__all__ = ["ScoreSection_OpacityHeadCreator"]
