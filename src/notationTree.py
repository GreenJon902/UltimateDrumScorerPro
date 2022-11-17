from __future__ import annotations

from kivy.event import EventDispatcher
from typing import Union




class MultipleNotes:
    parts: list[noteTree]

    def __init__(self, parts):
        self.parts = parts


class Note:
    names: list[str]

    def __init__(self, name):
        self.name = name


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



noteTree = Union[MultipleNotes, Note]

__all__ = ["noteTree", "Note", "MultipleNotes", "Bar"]
