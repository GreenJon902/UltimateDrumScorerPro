from kivy.graphics import InstructionGroup


class ScoreSection_StemCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self) -> InstructionGroup:
        raise NotImplementedError()

    def update_height(self, stem_group: InstructionGroup, stem_connection_point: float, height: float,
                      head_height: float):
        """
        Updates this stems height based of the given information. `stem_connection_point` doesn't specifically mean where
        it connects, but where it would connect should it go all the way.
        """
        raise NotImplementedError()


__all__ = ["ScoreSection_StemCreatorBase"]
