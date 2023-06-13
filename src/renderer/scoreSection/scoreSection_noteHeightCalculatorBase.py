class ScoreSection_NoteHeightCalculatorBase:
    def get(self, existent_notes_ids) -> tuple[list[tuple[float, float]], float]:
        """
        Returns a list containing note level and y level information. It also returns the height of all the heads.
        """
        raise NotImplementedError()


__all__ = ["ScoreSection_NoteHeightCalculatorBase"]
