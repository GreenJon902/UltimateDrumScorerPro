from typing import Optional

from kivy.graphics import InstructionGroup


class ScoreSection_HeadCreatorBase:
    def create(self, group: Optional[InstructionGroup], note_level_info: list[tuple[float, float]],
               nids: set[int]) -> tuple[InstructionGroup, float, Optional[int]]:
        """
        Creates or updates a head group for the given information, is group is None then a new one is created.
        The group returned is always the same object that was given. The width and lowest_note_id is also
        returned.
        """
        raise NotImplementedError()



__all__ = ["ScoreSection_HeadCreatorBase"]
