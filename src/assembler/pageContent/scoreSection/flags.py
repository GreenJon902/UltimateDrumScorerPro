from kivy.graphics import Line, Instruction, InstructionGroup, Color
from kivy.uix.widget import Widget

from score.notes import flag_width, flag_length, slanted_flag_length, slanted_flag_height_offset


def update_before_line_points(line: Line, widget: Widget):
    line.points = widget.right - flag_length, widget.y, widget.right, widget.y
    line.flag_update()


def draw_before_flag(widget: Widget) -> Instruction:
    ret = InstructionGroup()
    ret.add(Color(rgba=(0, 0, 0, 1)))
    line = Line(points=[widget.right - flag_length, widget.y, widget.right, widget.y], width=flag_width)
    widget.bind(pos=lambda _, _2: update_before_line_points(line, widget),
                right=lambda _, _2: update_before_line_points(line, widget))
    ret.add(line)
    return ret


def update_after_line_points(line: Line, widget: Widget):
    line.points = widget.x, widget.y, widget.x + flag_length, widget.y
    line.flag_update()


def draw_after_flag(widget: Widget) -> Instruction:
    ret = InstructionGroup()
    ret.add(Color(rgba=(0, 0, 0, 1)))
    line = Line(points=[widget.x, widget.y, widget.x + flag_length, widget.y], width=flag_width)
    widget.bind(pos=lambda _, _2: update_after_line_points(line, widget),
                right=lambda _, _2: update_after_line_points(line, widget))
    ret.add(line)
    return ret


def update_slanted_line_points(line: Line, widget: Widget):
    line.points = widget.x, widget.y, widget.x + slanted_flag_length * 2, widget.y - slanted_flag_height_offset
    line.flag_update()


def draw_slanted_flag(widget: Widget) -> Instruction:
    ret = InstructionGroup()
    ret.add(Color(rgba=(0, 0, 0, 1)))
    line = Line(points=[widget.x, widget.y, widget.x + slanted_flag_length, widget.y - slanted_flag_height_offset],
                width=flag_width)
    widget.bind(pos=lambda _, _2: update_slanted_line_points(line, widget),
                right=lambda _, _2: update_slanted_line_points(line, widget))
    ret.add(line)
    return ret
