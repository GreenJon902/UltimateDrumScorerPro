from kivy.graphics import InstructionGroup


class ScoreSection_BarCreatorBase:
    def create(self, note_ids) -> tuple[InstructionGroup, int, int]:
        raise NotImplementedError()


__all__ = ["ScoreSection_BarCreatorBase"]
