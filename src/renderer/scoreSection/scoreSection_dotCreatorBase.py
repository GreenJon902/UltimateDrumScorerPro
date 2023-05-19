from kivy.graphics import InstructionGroup


class ScoreSection_DotCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self, dots) -> tuple[InstructionGroup, int, int]:
        raise NotImplementedError()


__all__ = ["ScoreSection_DotCreatorBase"]
