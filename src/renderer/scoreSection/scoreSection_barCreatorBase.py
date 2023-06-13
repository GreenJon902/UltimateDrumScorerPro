from typing import Optional

from kivy.graphics import InstructionGroup


class ScoreSection_BarCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self, group: Optional[InstructionGroup], bars, before_bars, after_bars, slanted_bars) -> \
            tuple[InstructionGroup, float, float]:
        """
        Creates or updates a bar group for the given information, is group is None then a new one is created.
        The group returned is always the same object that was given. The minimum width and the height is also returned.
        """
        raise NotImplementedError()

    def update_width(self, bar_group: InstructionGroup, width: float):
        raise NotImplementedError()


__all__ = ["ScoreSection_BarCreatorBase"]
