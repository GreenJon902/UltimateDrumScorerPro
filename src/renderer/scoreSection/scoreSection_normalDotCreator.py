from kivy.graphics import InstructionGroup, Color, Ellipse

from kv import check_kv

check_kv()

from kv.settings import dot_radius, dot_spacing
from renderer.scoreSection.scoreSection_dotCreatorBase import ScoreSection_DotCreatorBase


class ScoreSection_NormalDotCreator(ScoreSection_DotCreatorBase):
    def create(self, dots) -> tuple[InstructionGroup, int, int]:
        group = InstructionGroup()
        group.add(Color(rgba=self.color))

        width = 0
        height = dot_radius * 2
        for n in range(dots):
            group.add(Ellipse(pos=(width, 0), size=(dot_radius * 2, dot_radius * 2)))
            width += dot_radius * 2 + dot_spacing
        if dots > 0:
            width -= dot_spacing

        return group, width, height


__all__ = ["ScoreSection_NormalDotCreator"]
