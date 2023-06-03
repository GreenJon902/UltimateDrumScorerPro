import os
from typing import Union

from kivy import Logger
from kivy.graphics import InstructionGroup
from kivy.properties import NumericProperty, StringProperty, ObjectProperty

from kv import check_kv
from kv.settings import st
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

    update_info: Union[str, list[str, int, tuple[int, str, ...]]] = ObjectProperty()

    def update(self, group: InstructionGroup, **kwargs):
        # Anyone trying to read this, im sorry, I really am. I tried my hardest :'( .  Wall have fun!! :)

        kwargs.setdefault("st", str(st))

        if self.update_info == "None":
            return
        elif self.update_info == "*":
            ii = 0  # Graphics instruction index
            for i, instruction in enumerate(self.instructions):
                ii = index_of_next_child_of_type(ii, group, instruction[0])
                update(group.children[ii], instruction[1], **kwargs)

        else:  # List so we have to do this a bit more complicated
            ii = 0  # Graphics instruction index
            for i, instruction in enumerate(self.instructions):
                name: str = instruction[0]
                attrs: dict[str, any] = instruction[1]

                if i in self.update_info or name in self.update_info:  # Index
                    ii = index_of_next_child_of_type(ii, group, instruction[0])
                    update(group.children[ii], attrs, **kwargs)
                else:
                    for kw, v in attrs.items():
                        if kw in self.update_info:
                            ii = index_of_next_child_of_type(ii, group, instruction[0])
                            v = format_value(v, **kwargs)
                            setattr(group.children[ii], kw, v)

                    # Where we want specific attributes of a specific instruction (e.g. height of instruction 3)
                    for item in self.update_info:
                        if isinstance(item, tuple) or isinstance(item, list):  # JSON has no tuple so list too
                            i2 = item[0]
                            if i == i2:
                                for attr_name in item[1:]:
                                    if attr_name in attrs.keys():
                                        v = attrs[attr_name]
                                        v = format_value(v, **kwargs)

                                        ii = index_of_next_child_of_type(ii, group, instruction[0])
                                        setattr(group.children[ii], attr_name, v)


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
