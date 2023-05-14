from kivy.graphics import InstructionGroup


class ScoreSection_DecorationCreatorBase:
    def create(self, note_ids) -> tuple[InstructionGroup, int, int]:
        raise NotImplementedError()


__all__ = ["ScoreSection_DecorationCreatorBase"]
