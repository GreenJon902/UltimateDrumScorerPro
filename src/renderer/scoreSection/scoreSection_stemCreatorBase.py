from kivy.graphics import InstructionGroup


class ScoreSection_StemCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self) -> InstructionGroup:
        raise NotImplementedError()

    def update_height(self, stem_group: InstructionGroup, note_height: float, stem_connection_offset: float,
                      height: float, head_height: float):
        """
        Updates this stems height based of the given information.
        """
        raise NotImplementedError()


__all__ = ["ScoreSection_StemCreatorBase"]
