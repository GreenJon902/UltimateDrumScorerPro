from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from typing import Union
    from noteTree.note import Note


class MultipleNotes:
    parts: list[Union[Note, MultipleNotes]]

    def __init__(self, parts):
        self.parts = parts
