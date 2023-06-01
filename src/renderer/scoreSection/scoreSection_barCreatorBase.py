from kivy.graphics import InstructionGroup


class ScoreSection_BarCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self, bars, before_bars, after_bars, slanted_bars) -> tuple[InstructionGroup, int, int]:
        raise NotImplementedError()

    def update_width(self, bar_group: InstructionGroup, width: float):
        raise NotImplementedError()


__all__ = ["ScoreSection_BarCreatorBase"]
