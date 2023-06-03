from kivy.graphics import InstructionGroup

from kv import check_kv
from renderer.scoreSection.scoreSection_decorationCreatorBase import ScoreSection_DecorationCreatorBase
from scoreSectionDesigns.decorations import decorations, check_decorations

check_kv()
check_decorations()


class ScoreSection_NormalDecorationCreator(ScoreSection_DecorationCreatorBase):
    def create(self, did) -> tuple[InstructionGroup, float, float]:
        if did is None:
            return None

        group = decorations[did].make_canvas(head_height=decorations[did].min_height,
                                             height=decorations[did].min_height)

        return group, decorations[did].width, decorations[did].min_height

    def update_height(self, decoration_group, head_height, overall_height, did):
        if did is None:
            return
        decorations[did].update(decoration_group, head_height=head_height, height=overall_height)


__all__ = ["ScoreSection_NormalDecorationCreator"]
