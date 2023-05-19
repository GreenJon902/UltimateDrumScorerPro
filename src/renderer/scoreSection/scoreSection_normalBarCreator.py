from kivy.graphics import InstructionGroup, PushMatrix, Color, PopMatrix, Line, Translate

from kv import check_kv
from renderer.scoreSection.scoreSection_barCreatorBase import ScoreSection_BarCreatorBase

check_kv()

from kv.settings import st, half_bar_length, bar_height


class ScoreSection_NormalBarCreator(ScoreSection_BarCreatorBase):
    def create(self, bars, before_bars, after_bars) -> tuple[InstructionGroup, int, int]:
        group = InstructionGroup()
        group.add(PushMatrix())
        group.add(Color(rgba=self.color))

        width = 0 + (0 if before_bars < 0 else half_bar_length) + (0 if after_bars < 0 else half_bar_length)  # if not
                                                                                                        # updated later

        bar_group = InstructionGroup()
        for bar in range(bars):
            bar_group.add(Line(points=(0, bar_height / 2, width, bar_height / 2), width=st))
            bar_group.add(Translate(0, bar_height / 2))

        before_bar_group = InstructionGroup()
        for bar in range(before_bars):
            before_bar_group.add(Line(points=(0, bar_height / 2, half_bar_length, bar_height / 2), width=st))
            before_bar_group.add(Translate(0, bar_height / 2))

        after_bar_group = InstructionGroup()
        for bar in range(after_bars):
            after_bar_group.add(Line(points=(width - half_bar_length, bar_height / 2, width, bar_height / 2), width=st))
            after_bar_group.add(Translate(0, bar_height / 2))

        height = bars * bar_height + before_bars * bar_height + after_bars * bar_height

        group.add(after_bar_group)
        group.add(before_bar_group)
        group.add(bar_group)
        group.add(PopMatrix())
        return group, width, height


__all__ = ["ScoreSection_NormalBarCreator"]
