from typing import Optional

from kivy.graphics import InstructionGroup


class ScoreSection_DotCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self, group: Optional[InstructionGroup], dots: int) -> tuple[InstructionGroup, float, float]:
        """
        Creates or updates a dot group for the given information, is group is None then a new one is created.
        The group returned is always the same object that was given. The width and height are also returned.
        """
        raise NotImplementedError()


__all__ = ["ScoreSection_DotCreatorBase"]
