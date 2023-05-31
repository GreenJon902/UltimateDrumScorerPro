from kivy.graphics import InstructionGroup, Translate, PushMatrix, PopMatrix

from renderer.scoreSection.scoreSection_componentOrganiserBase import ScoreSection_ComponentOrganiserBase


def default(x, default_):  # Get instruction group from info with a default
    if x is None:
        x = default_
    return x


class ScoreSection_NormalComponentOrganiser(ScoreSection_ComponentOrganiserBase):
    def add_section(self, group: InstructionGroup, index, head_info=None, bar_info=None, dot_info=None):
        head_info = default(head_info, (InstructionGroup(), 0, 0))
        bar_info = default(bar_info, (InstructionGroup(), 0, 0))
        dot_info = default(dot_info, (InstructionGroup(), 0, 0))

        width = max(head_info[1], bar_info[1], dot_info[1])

        section_group = InstructionGroup()
        section_group.add(PushMatrix())

        section_group.add(PushMatrix())
        section_group.add(Translate(width - head_info[1], 0))
        section_group.add(head_info[0])
        section_group.add(PopMatrix())

        section_group.add(Translate(0, head_info[2]))

        section_group.add(PushMatrix())
        section_group.add(Translate(width - bar_info[1], 0))
        section_group.add(bar_info[0])
        section_group.add(PopMatrix())

        section_group.add(Translate(0, bar_info[2]))
        section_group.add(dot_info[0])

        section_group.add(PopMatrix())
        section_group.add(Translate(width, 0))  # X
        group.insert(index + 1, section_group)  # + 1 as push matrix

    def setup(self, group: InstructionGroup):
        group.clear()
        group.add(PushMatrix())
        group.add(PopMatrix())


__all__ = ["ScoreSection_NormalComponentOrganiser"]
