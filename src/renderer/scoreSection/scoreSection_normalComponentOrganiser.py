from kivy.graphics import InstructionGroup, Translate, PushMatrix, PopMatrix

from kv.settings import bar_height
from renderer.scoreSection.scoreSection_componentOrganiserBase import ScoreSection_ComponentOrganiserBase


def default(x, default_):  # Get instruction group from info with a default
    if x is None:
        x = default_
    return x


class ScoreSection_NormalComponentOrganiser(ScoreSection_ComponentOrganiserBase):
    to_top_translate: Translate  # Moves from y=0 to the top of the score section

    def __init__(self, *args, **kwargs):
        ScoreSection_ComponentOrganiserBase.__init__(self, *args, **kwargs)
        self.to_top_translate = Translate(0, 0)

    def add_section(self, index, head_info=None, bar_info=None, dot_info=None, stem_info=None):
        head_info = default(head_info, (InstructionGroup(), 0, 0))
        bar_info = default(bar_info, (InstructionGroup(), 0, 0))
        dot_info = default(dot_info, (InstructionGroup(), 0, 0))
        stem_info = default(stem_info, (InstructionGroup(), 0))

        width = max(head_info[1], bar_info[1], dot_info[1])
        height = head_info[2] + bar_info[2] + dot_info[2]

        if height > self.to_top_translate.y:
            self.to_top_translate.y = height

        section_group = InstructionGroup()

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
        section_group.add(Translate(0, -bar_info[2] + bar_height / 2))
        section_group.add(bar_info[0])
        section_group.add(PopMatrix())


        # Finishing
        section_group.add(Translate(width + stem_info[1], 0))
        self.group.insert(index + 1, section_group)  # + 1 as push matrix

        return_instruction = []
        if width != bar_info[1]:
            return_instruction.append((["update_bar_width", bar_info[0], width], {}))

        return return_instruction

    def setup(self, group: InstructionGroup):
        group.clear()
        group.add(PushMatrix())
        group.add(PopMatrix())

        self.group = group


__all__ = ["ScoreSection_NormalComponentOrganiser"]
