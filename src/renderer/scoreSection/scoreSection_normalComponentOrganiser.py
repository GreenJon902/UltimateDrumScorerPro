from kivy.graphics import InstructionGroup, Translate, PushMatrix, PopMatrix

from kv import check_kv

check_kv()

from kv.settings import bar_height
from renderer.scoreSection.scoreSection_componentOrganiserBase import ScoreSection_ComponentOrganiserBase


def default(x, default_):  # Get instruction group from info with a default
    if x is None:
        x = default_
    return x


class ScoreSection_NormalComponentOrganiser(ScoreSection_ComponentOrganiserBase):
    parent_group: InstructionGroup
    to_top_translate: Translate  # Moves from y=0 to the top of the score section
    widths: list[float]

    def __init__(self, *args, **kwargs):
        self.widths = []
        self.to_top_translate = Translate(0, 0)
        ScoreSection_ComponentOrganiserBase.__init__(self, *args, **kwargs)

    def add_section(self, index, head_info=None, bar_info=None, dot_info=None, stem_info=None, decoration_info=None):
        return_instructions = []

        head_info = default(head_info, (InstructionGroup(), 0, 0))
        bar_info = default(bar_info, (InstructionGroup(), 0, 0))
        dot_info = default(dot_info, (InstructionGroup(), 0, 0))
        stem_info = default(stem_info, (InstructionGroup(), 0))
        decoration_info = default(decoration_info, (InstructionGroup(), 0, 0))

        width = max(head_info[1], bar_info[1], dot_info[1]) + decoration_info[1]
        height = head_info[2] + bar_info[2] + dot_info[2]

        if height < decoration_info[2]:
            height = decoration_info[2]

        if height > self.to_top_translate.y:
            self.to_top_translate.y = height
            for i, child in enumerate(self.group.children):
                return_instructions.append((["update_stem_height", child.children[11], self.to_top_translate.y, i], {}))

        section_group = InstructionGroup()

        # Decorations
        section_group.add(decoration_info[0])

        # Heads
        section_group.add(PushMatrix())
        section_group.add(Translate(width - head_info[1], 0))
        section_group.add(head_info[0])

        # Dots
        section_group.add(Translate(-(width - head_info[1]), head_info[2]))
        section_group.add(dot_info[0])
        section_group.add(PopMatrix())

        # Stems
        section_group.add(PushMatrix())
        section_group.add(self.to_top_translate)
        section_group.add(PushMatrix())
        section_group.add(Translate(width, 0))
        section_group.add(stem_info[0])

        # Bars
        section_group.add(PopMatrix())
        section_group.add(Translate(-stem_info[1] / 2, -bar_info[2] + bar_height / 2))
        section_group.add(bar_info[0])
        section_group.add(PopMatrix())


        # Finishing
        section_group.add(Translate(width + stem_info[1], 0))
        self.group.insert(index, section_group)
        self.widths.insert(index, width)


        if width != bar_info[1]:
            return_instructions.append((["update_bar_width", bar_info[0], width + stem_info[1]], {}))
        if height != decoration_info[2]:
            return_instructions.append((["update_decoration_height", decoration_info[0], head_info[2], height, index],
                                        {}))
        return_instructions.append((["update_stem_height", stem_info[0], self.to_top_translate.y, index], {}))
        return_instructions.append((["set_size", *self.get_size()], {}))

        return return_instructions

    def setup(self, parent_group: InstructionGroup):
        parent_group.clear()
        parent_group.add(PushMatrix())
        group = InstructionGroup()
        parent_group.add(group)
        parent_group.add(PopMatrix())

        self.parent_group = parent_group
        self.group = group

    def get_size(self):
        return sum(self.widths), self.to_top_translate.y


__all__ = ["ScoreSection_NormalComponentOrganiser"]
