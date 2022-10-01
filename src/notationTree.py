from __future__ import annotations

from kivy.event import EventDispatcher
from typing import Union




class MultipleNotes:
    parts: list[noteTree]

    def __init__(self, parts):
        self.parts = parts

    def flatten(self):  # First part of flattening
        flattened = list()

        my_depth = len(self.parts)
        for part in self.parts:
            for part_flattened_part in part.flatten():
                flattened.append((part_flattened_part[0] * my_depth, part_flattened_part[1]))

        return flattened



class Notes:
    names: list[str]

    def __init__(self, *names):
        self.names = list(names)

    def flatten(self):
        return [(1, self.names)]


class Bar:
    measureLength: int  # top number - beats in bar
    subdivisionQuantifier: int  # bottom number
    _content: list[noteTree]

    @staticmethod
    def empty(measureLength, subdivisionQuantifier):
        bar = Bar()

        bar._content = [None for i in range(measureLength)]
        bar.subdivisionQuantifier = subdivisionQuantifier

        return bar

    @staticmethod
    def fromList(content, subdivisionQuantifier):
        bar = Bar()

        bar._content = content
        bar.subdivisionQuantifier = subdivisionQuantifier

        return bar

    @property
    def measureLength(self):
        return len(self._content)

    def getContent(self):
        return self._content



noteTree = Union[MultipleNotes, Notes]

__all__ = ["noteTree", "Notes", "MultipleNotes", "Bar"]
