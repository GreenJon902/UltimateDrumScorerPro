from kivy.graphics import InstructionGroup, Color, Canvas

from kv import check_kv
from renderer.scoreSection.scoreSection_decorationCreatorBase import ScoreSection_DecorationCreatorBase
from scoreSectionDesigns.decorations import decorations, check_decorations

check_kv()
check_decorations()


class ScoreSection_NormalDecorationCreator(ScoreSection_DecorationCreatorBase):
    def create(self, group, did) -> tuple[InstructionGroup, float, float]:
        if group is None:
            group = Canvas()  # So we can do with statement

        group.clear()
        group.add(Color(rgba=self.color))

        if did is None:
            return group, 0, 0

        with group:
            decorations[did].draw(head_height=decorations[did].min_height, height=decorations[did].min_height)

        return group, decorations[did].width, decorations[did].min_height

    def update_height(self, group, overall_height, head_height, did):
        if did is None:
            return
        decorations[did].update(group, head_height=head_height, height=overall_height)


__all__ = ["ScoreSection_NormalDecorationCreator"]
