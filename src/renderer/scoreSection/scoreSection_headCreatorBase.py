from kivy.graphics import InstructionGroup


class ScoreSection_HeadCreatorBase:
    def create(self, present_note_ids, existent_notes_ids) -> tuple[InstructionGroup, int, int, tuple[float, int]]:
        raise NotImplementedError()

    def update(self, present_note_ids, existent_notes_ids, instructionGroup) -> tuple[InstructionGroup, int, int,
                                                                                      tuple[float, int]]:
        raise NotImplementedError()


__all__ = ["ScoreSection_HeadCreatorBase"]
