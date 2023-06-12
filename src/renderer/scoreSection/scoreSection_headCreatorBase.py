from kivy.graphics import InstructionGroup


class ScoreSection_HeadCreatorBase:
    def create(self, present_note_ids, note_levels) -> tuple[InstructionGroup, int, int, tuple[float, int]]:
        raise NotImplementedError()

    """
    Group is returned for consistency, it should not change (children can through).
    """
    def update(self, present_note_ids, note_levels, instructionGroup) -> tuple[InstructionGroup, int, int, tuple[float, int]]:
        raise NotImplementedError()


__all__ = ["ScoreSection_HeadCreatorBase"]
