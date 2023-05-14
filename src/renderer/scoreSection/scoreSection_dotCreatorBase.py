from kivy.graphics import InstructionGroup


class ScoreSection_DotCreatorBase:
    def create(self, note_ids) -> tuple[InstructionGroup, int, int]:
        raise NotImplementedError()


__all__ = ["ScoreSection_DotCreatorBase"]
