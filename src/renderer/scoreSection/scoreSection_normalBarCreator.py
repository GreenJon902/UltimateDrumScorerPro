from kivy.graphics import InstructionGroup, Color, Line

from kv import check_kv
from renderer.scoreSection.scoreSection_barCreatorBase import ScoreSection_BarCreatorBase

check_kv()

from kv.settings import st, half_bar_length, bar_height


class ScoreSection_NormalBarCreator(ScoreSection_BarCreatorBase):
    def create(self, bars, before_bars, after_bars) -> tuple[InstructionGroup, int, int]:
        group = InstructionGroup()
        group.add(Color(rgba=self.color))

        width = 0 + (0 if before_bars < 0 else half_bar_length) + (0 if after_bars < 0 else half_bar_length)  # if not
                                                                                                        # updated later
        y = bar_height / 2

        after_bar_group = InstructionGroup()
        for bar in range(after_bars):
            after_bar_group.add(Line(points=(width - half_bar_length, y, width, y), width=st))
            y += bar_height

        before_bar_group = InstructionGroup()
        for bar in range(before_bars):
            before_bar_group.add(Line(points=(0, y, half_bar_length, y), width=st))
            y += bar_height

        bar_group = InstructionGroup()
        for bar in range(bars):
            bar_group.add(Line(points=(0, y, width, y), width=st))
            y += bar_height

        height = y - bar_height / 2

        group.add(after_bar_group)
        group.add(before_bar_group)
        group.add(bar_group)
        return group, width, height

    def update_width(self, bar_group: InstructionGroup, width: float):
        print(bar_group.children)
        after_bar_group = bar_group.children[1]
        full_bar_group = bar_group.children[3]

        for bar in after_bar_group.children:
            if isinstance(bar, Line):
                bar.points[0] = width - half_bar_length
                bar.points[2] = width

        for bar in full_bar_group.children:
            if isinstance(bar, Line):
                bar.points[2] = width



__all__ = ["ScoreSection_NormalBarCreator"]
