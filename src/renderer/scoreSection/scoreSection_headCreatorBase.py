from kivy.graphics import InstructionGroup


class ScoreSection_HeadCreatorBase:
    present_color: tuple[float, float, float, float]
    absent_color: tuple[float, float, float, float]

    def __init__(self, present_color, absent_color):
        self.present_color = present_color
        self.absent_color = absent_color

    def create(self, present_note_ids, existent_notes_ids) -> tuple[InstructionGroup, int, int]:
        raise NotImplementedError()

    def update(self, present_note_ids, existent_notes_ids, instructionGroup) -> tuple[InstructionGroup, int, int]:
        raise NotImplementedError()


__all__ = ["ScoreSection_HeadCreatorBase"]
