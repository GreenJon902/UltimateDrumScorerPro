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
    def __init__(self, *args, **kwargs):
        ScoreSection_ComponentOrganiserBase.__init__(self, *args, **kwargs)

    def build(self, head_group=None, bar_group=None, dot_group=None):
        head_group = default(head_group, InstructionGroup())
        bar_group = default(bar_group, InstructionGroup())
        dot_group = default(dot_group, InstructionGroup())


        section_group = InstructionGroup()

        # Heads
        g = InstructionGroup()
        g.add(PushMatrix())
        g.add(Translate())
        g.add(head_group)
        g.add(PopMatrix())
        section_group.add(g)

        # Dots
        g = InstructionGroup()
        g.add(PushMatrix())
        g.add(Translate())
        g.add(dot_group)
        g.add(PopMatrix())
        section_group.add(g)

        # Bars
        g = InstructionGroup()
        g.add(PushMatrix())
        g.add(Translate())
        g.add(bar_group)
        g.add(PopMatrix())
        section_group.add(g)

        # Translate
        section_group.add(Translate())

        return section_group

    def parent_insert(self, group: InstructionGroup, index: int, built_group: InstructionGroup):
        group.insert(index + 1, built_group)  # +1 because of PushMatrix()

    def organise(self, ssihs, head_height):
        heads = 0
        dots = 1
        bars = 2
        ending_trans = 3

        trans = 1

        max_dot_height = max(ssihs, key=lambda x: x.dot_height).dot_height
        max_bar_height = max(ssihs, key=lambda x: x.bar_height).bar_height

        height = head_height + max_dot_height + max_bar_height

        for ssih in ssihs:
            width = max(ssih.head_width, ssih.dot_width, ssih.bar_width_min, ssih.custom_width)

            ssih.built_group.children[heads].children[trans].x = width - ssih.head_width
            ssih.built_group.children[dots].children[trans].y = head_height + max_dot_height - ssih.dot_height
            ssih.built_group.children[bars].children[trans].y = height - ssih.bar_height

            ssih.built_group.children[ending_trans].x = width


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
                return_instructions.append((["update_decoration_height", child.children[0], head_info[2],
                                             self.to_top_translate.y, i], {}))

        section_group = InstructionGroup()

        # Decorations
        section_group.add(decoration_info[0])

        # Heads
        section_group.add(PushMatrix())
        section_group.add(Translate(width - head_info[1], 0))
        section_group.add(3)

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
        return_instructions.append((["set_size", *self.get_size()], {}))

        return return_instructions

    def setup(self, parent_group: InstructionGroup):
        parent_group.clear()
        parent_group.add(PushMatrix())
        parent_group.add(Translate())  # Breaks otherwise
        parent_group.add(PopMatrix())


    def get_size(self):
        return sum(self.widths), self.to_top_translate.y


__all__ = ["ScoreSection_NormalComponentOrganiser"]
