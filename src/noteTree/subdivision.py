from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from typing import Union
    from noteTree.note import Note


class Subdivision:
    parts: list[Union[Note, Subdivision]]

    def __init__(self, parts):
        self.parts = parts
