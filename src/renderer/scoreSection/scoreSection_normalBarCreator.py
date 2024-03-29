from kivy.graphics import InstructionGroup, Color, Line

from kv import check_kv
from renderer.scoreSection.scoreSection_barCreatorBase import ScoreSection_BarCreatorBase

check_kv()

from kv.settings import st, half_bar_length, bar_height, slanted_flag_length, slanted_flag_height_offset


class ScoreSection_NormalBarCreator(ScoreSection_BarCreatorBase):
    def create(self, group, bars, before_bars, after_bars, slanted_bars):
        if group is None:
            group = InstructionGroup()

        group.clear()
        group.add(Color(rgba=self.color))

        width = (0 +  # incase not updated later
                 (0 if before_bars <= 0 else half_bar_length) +
                 (0 if after_bars <= 0 else half_bar_length))
        if slanted_bars > 0 and width < slanted_flag_length:
            width = slanted_flag_length

        y = bar_height

        slanted_bar_group, y = self.make_slanted(slanted_bars, y, width)
        after_bar_group, y = self.make_after(after_bars, y, width)
        before_bar_group, y = self.make_before(before_bars, y, width)
        bar_group, y = self.make_full(bars, y, width)

        height = y - bar_height

        group.add(slanted_bar_group)
        group.add(after_bar_group)
        group.add(before_bar_group)
        group.add(bar_group)
        return group, width, height

    def make_slanted(self, slanted_bars, y, width):
        if slanted_bars > 0:
            y += slanted_flag_height_offset  # Slanted flags are taller than bars
        slanted_bar_group = InstructionGroup()
        for bar in range(slanted_bars):
            slanted_bar_group.add(Line(points=(0, y, slanted_flag_length, y-slanted_flag_height_offset), width=st))
            y += bar_height
        return slanted_bar_group, y

    def make_after(self, after_bars, y, width):
        after_bar_group = InstructionGroup()
        for bar in range(after_bars):
            after_bar_group.add(Line(points=(width - half_bar_length, y, width, y), width=st))
            y += bar_height
        return after_bar_group, y

    def make_before(self, before_bars, y, width):
        before_bar_group = InstructionGroup()
        for bar in range(before_bars):
            before_bar_group.add(Line(points=(0, y, half_bar_length, y), width=st))
            y += bar_height
        return before_bar_group, y

    def make_full(self, bars, y, width):
        bar_group = InstructionGroup()
        for bar in range(bars):
            bar_group.add(Line(points=(0, y, width, y), width=st))
            y += bar_height
        return bar_group, y

    def update_width(self, bar_group, width):
        after_bar_group = bar_group.children[2]
        full_bar_group = bar_group.children[4]

        for bar in after_bar_group.children:
            if isinstance(bar, Line):
                bar.points[0] = width - half_bar_length
                bar.points[2] = width

        for bar in full_bar_group.children:
            if isinstance(bar, Line):
                bar.points[2] = width



__all__ = ["ScoreSection_NormalBarCreator"]
