from kivy.graphics import InstructionGroup, Color, Line

from kv import check_kv
from renderer.scoreSection.scoreSection_stemCreatorBase import ScoreSection_StemCreatorBase
from scoreSectionDesigns.notes import notes

check_kv()

from kv.settings import st, stem_width


class ScoreSection_NormalStemCreator(ScoreSection_StemCreatorBase):
    def create(self) -> tuple[InstructionGroup, int]:
        group = InstructionGroup()
        group.add(Color(rgba=self.color))

        width = stem_width
        group.add(Line(points=(width / 2, 0, width / 2, 10), width=st))  # Default height of 10 so can be seen during
                                                                         # testing, will be overwritten

        return group, width

    def update_height(self, stem_group, lowest_note_info):
        if lowest_note_info is None:
            y = 0
            stem_group.children[0].a = 0
        else:
            y = lowest_note_info[0] + notes[lowest_note_info[1]].stem_connection_offset
            print(y)
            stem_group.children[0].a = 1
        stem_group.children[2].points[3] = y  # Use index 2 as 0 is color, 1 is bind texture that happens
                                              # automatically

__all__ = ["ScoreSection_NormalStemCreator"]
