from kivy.graphics import InstructionGroup, Translate, PushMatrix, PopMatrix

from kv import check_kv

check_kv()

from renderer.scoreSection.scoreSection_componentOrganiserBase import ScoreSection_ComponentOrganiserBase


def default(x, default_):  # Get instruction group from info with a default
    if x is None:
        x = default_
    return x


class ScoreSection_NormalComponentOrganiser(ScoreSection_ComponentOrganiserBase):
    def __init__(self, *args, **kwargs):
        ScoreSection_ComponentOrganiserBase.__init__(self, *args, **kwargs)

    def build(self, head_group=None, bar_group=None, dot_group=None, stem_group=None, decoration_group=None):
        head_group = default(head_group, InstructionGroup())
        bar_group = default(bar_group, InstructionGroup())
        dot_group = default(dot_group, InstructionGroup())
        stem_group = default(stem_group, InstructionGroup())
        decoration_group = default(decoration_group, InstructionGroup())


        section_group = InstructionGroup()

        # Heads
        g = InstructionGroup()
        g.add(PushMatrix())
        g.add(Translate())
        g.add(decoration_group)
        g.add(PopMatrix())
        section_group.add(g)

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

        # Stems
        g = InstructionGroup()
        g.add(PushMatrix())
        g.add(Translate())
        g.add(stem_group)
        g.add(PopMatrix())
        section_group.add(g)

        # Translate
        section_group.add(Translate())

        return section_group

    def parent_insert(self, group: InstructionGroup, index: int, built_group: InstructionGroup):
        group.insert(index + 1, built_group)  # +1 because of PushMatrix()

    def parent_remove(self, group: InstructionGroup, index: int):
        group.remove(group.children[index + 1])  # +1 because of PushMatrix()

    def organise(self, ssihs, head_height):
        if len(ssihs) == 0:
            return 0, 0, []

        decorations = 0
        heads = 1
        dots = 2
        bars = 3
        stems = 4
        ending_trans = 5

        trans = 1

        max_dot_height = max(ssihs, key=lambda x: x.dot_height).dot_height
        max_bar_height = max(ssihs, key=lambda x: x.bar_height).bar_height
        max_decoration_height = max(ssihs, key=lambda x: x.decoration_height_min).decoration_height_min

        height = max(head_height + max_dot_height + max_bar_height, max_decoration_height)

        section_widths = list()

        for ssih in ssihs:
            width = max(ssih.head_width, ssih.dot_width, ssih.bar_width_min, ssih.custom_width) + ssih.decoration_width
            section_widths.append(width)

            ssih.built_group.children[heads].children[trans].x = width - ssih.head_width
            ssih.built_group.children[dots].children[trans].y = head_height + max_dot_height - ssih.dot_height
            ssih.built_group.children[bars].children[trans].y = height - ssih.bar_height
            ssih.built_group.children[stems].children[trans].x = width
            ssih.built_group.children[stems].children[trans].y = height

            ssih.built_group.children[ending_trans].x = width

        return sum(section_widths), height, section_widths

    def setup(self, parent_group: InstructionGroup):
        parent_group.clear()
        parent_group.add(PushMatrix())
        parent_group.add(Translate())  # Breaks otherwise
        parent_group.add(PopMatrix())


    def get_size(self):
        return sum(self.widths), self.to_top_translate.y


__all__ = ["ScoreSection_NormalComponentOrganiser"]
