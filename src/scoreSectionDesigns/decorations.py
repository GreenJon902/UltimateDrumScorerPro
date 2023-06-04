import os

from kivy import Logger
from kivy.graphics import InstructionGroup
from kivy.properties import NumericProperty, StringProperty

from kv import check_kv
from scoreSectionDesigns import read_design_from, Design, format_value

check_kv()

path = os.path.join(os.path.split(os.path.abspath(__file__))[0], "../designs/decorations")


def update(group, attrs, **kwargs):
    for kw, v in attrs.items():
        print(group, attrs, kwargs, kw, v)
        v = format_value(v, **kwargs)
        setattr(group, kw, v)


def index_of_next_child_of_type(before_index: int, group: InstructionGroup, name: str):  # Because sometimes bind
                                                                                         # textures and stuff are added
    i = before_index
    while i < len(group.children) and type(group.children[i]).__name__ != name:
        i += 1
    return i


class Decoration(Design):
    width: float = NumericProperty()
    min_height: float = NumericProperty()

    name: str = StringProperty()

    def update(self, group: InstructionGroup, **kwargs):
        ii = 0  # Graphics instruction index
        for i, instruction in enumerate(self.instructions):
            ii = index_of_next_child_of_type(ii, group, instruction[0])
            update(group.children[ii], instruction[1], **kwargs)



decorations_loaded = False
decorations: dict[int, Decoration] = {}


def check_decorations():
    global decorations_loaded

    if not decorations_loaded:
        Logger.info("UDSP: Loading decoration files...")
        for note_path in os.listdir(path):
            did, decoration = read_design_from(os.path.join(path, note_path), Decoration)
            if did in decorations:
                Logger.warning(f"Decorations: Already has note for id {did}, {decorations[did]} {decoration}")
            decorations[did] = decoration
        decorations_loaded = True


__all__ = ["Decoration", "check_decorations", "decorations"]
