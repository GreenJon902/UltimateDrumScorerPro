from kivy import Logger
from kivy.graphics import InstructionGroup, Color, Line

from kv import check_kv
from renderer.scoreSection.scoreSection_stemCreatorBase import ScoreSection_StemCreatorBase

check_kv()

from kv.settings import st


class ScoreSection_NormalStemCreator(ScoreSection_StemCreatorBase):
    def create(self):
        group = InstructionGroup()
        group.add(Color(rgba=self.color))

        group.add(Line(points=(0, 0, 0, 10), width=st))  # Default height of 10 so can be seen during testing, will be
                                                         # overwritten

        return group

    def update_height(self, stem_group, note_height, stem_connection_offset, height, head_height):
        if stem_connection_offset is None:
            Logger.warning("ScoreSection_NormalStemCreator: stem_connection_offset was None, defaulting to 0")
            stem_connection_offset = 0

        if note_height is None:
            y = 0
            stem_group.children[0].a = 0
        else:
            y = note_height + stem_connection_offset - height
            stem_group.children[0].a = 1
        stem_group.children[2].points[3] = y  # Use index 2 as 0 is color, 1 is bind texture that happens
                                              # automatically
        stem_group.children[2].flag_update()




__all__ = ["ScoreSection_NormalStemCreator"]
