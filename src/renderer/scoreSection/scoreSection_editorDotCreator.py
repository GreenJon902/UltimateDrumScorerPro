from kivy.graphics import InstructionGroup, Color

from kv import check_kv
from renderer.scoreSection.scoreSection_normalDotCreator import ScoreSection_NormalDotCreator

check_kv()


class ScoreSection_EditorDotCreator(ScoreSection_NormalDotCreator):
    present_color: tuple[float, float, float, float]
    absent_color: tuple[float, float, float, float]

    def __init__(self, present_color, absent_color):
        self.present_color = present_color
        self.absent_color = absent_color

    def create(self, group, dots):
        if group is None:
            group = InstructionGroup()

        group.clear()

        if dots == 0:
            group.add(Color(rgba=self.absent_color))
            group, width, height = self.make(group, 1)
        else:
            group.add(Color(rgba=self.present_color))
            group, width, height = self.make(group, dots)

        return group, width, height


__all__ = ["ScoreSection_EditorDotCreator"]
