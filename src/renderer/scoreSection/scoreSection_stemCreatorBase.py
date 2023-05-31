from kivy.graphics import InstructionGroup


class ScoreSection_StemCreatorBase:
    color: tuple[float, float, float, float]

    def __init__(self, color):
        self.color = color

    def create(self) -> tuple[InstructionGroup, int]:
        raise NotImplementedError()

    """
    Updates this stems height based of the stem offset and y level of the note info given. Also takes the previous stem
    info
    """
    def update_height(self, stem_info: tuple[InstructionGroup, int], note_info: tuple[float, int]):
        raise NotImplementedError()


__all__ = ["ScoreSection_StemCreatorBase"]
