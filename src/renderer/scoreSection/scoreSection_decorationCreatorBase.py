from kivy.graphics import InstructionGroup


class ScoreSection_DecorationCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self, decoration_id) -> tuple[InstructionGroup, int, int]:
        """
        Decoration ID can be None meaning no decoration. Returned height is minimum height.
        """
        raise NotImplementedError()

    def update_height(self, decoration_group, head_height, overall_height, did):
        """
        Height doesn't have to change as some decorations don't scale fully.
        Decoration ID can still be None.
        """
        raise NotImplementedError()


__all__ = ["ScoreSection_DecorationCreatorBase"]
