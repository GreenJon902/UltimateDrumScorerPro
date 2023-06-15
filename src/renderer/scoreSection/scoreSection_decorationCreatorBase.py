from kivy.graphics import InstructionGroup


class ScoreSection_DecorationCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self, group: InstructionGroup, decoration_id: int) -> tuple[InstructionGroup, int, int]:
        """
        Decoration ID can be None meaning no decoration. Returns width and minimum height
        """
        raise NotImplementedError()

    def update_height(self, group, overall_height, head_height, did):
        """
        Height doesn't have to change as some decorations don't scale fully.
        Decoration ID can still be None.
        """
        raise NotImplementedError()


__all__ = ["ScoreSection_DecorationCreatorBase"]
