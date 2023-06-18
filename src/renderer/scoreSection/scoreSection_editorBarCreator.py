from kivy.graphics import InstructionGroup, Color, Line

from kv import check_kv
from renderer.scoreSection.scoreSection_normalBarCreator import ScoreSection_NormalBarCreator

check_kv()

from kv.settings import half_bar_length, bar_height, slanted_flag_length


class ScoreSection_EditorBarCreator(ScoreSection_NormalBarCreator):
    present_color: tuple[float, float, float, float]
    absent_color: tuple[float, float, float, float]

    def __init__(self, present_color, absent_color):
        self.present_color = present_color
        self.absent_color = absent_color

    def create(self, group, bars, before_bars, after_bars, slanted_bars):
        if group is None:
            group = InstructionGroup()

        group.clear()

        width = (0 +  # incase not updated later
                 (0 if before_bars <= 0 else half_bar_length) +
                 (0 if after_bars <= 0 else half_bar_length))
        if slanted_bars > 0 and width < slanted_flag_length:
            width = slanted_flag_length

        y = bar_height

        y = self.editor_make(group, self.make_slanted, slanted_bars, y, width)
        y = self.editor_make(group, self.make_before, before_bars, y, width)
        y = self.editor_make(group, self.make_after, after_bars, y, width)
        y = self.editor_make(group, self.make_full, bars, y, width)

        height = y - bar_height
        return group, width, height

    def editor_make(self, group, func, n, y, width):
        if n == 0:
            group.add(Color(rgba=self.absent_color))
            new_group, y = func(1, y, width)
            y += bar_height
        else:
            group.add(Color(rgba=self.present_color))
            new_group, y = func(n, y, width)
        group.add(new_group)
        return y

    def update_width(self, bar_group, width):
        after_bar_group = bar_group.children[5]
        full_bar_group = bar_group.children[7]

        for bar in after_bar_group.children:
            if isinstance(bar, Line):
                bar.points[0] = width - half_bar_length
                bar.points[2] = width

        for bar in full_bar_group.children:
            if isinstance(bar, Line):
                bar.points[2] = width


__all__ = ["ScoreSection_EditorBarCreator"]
