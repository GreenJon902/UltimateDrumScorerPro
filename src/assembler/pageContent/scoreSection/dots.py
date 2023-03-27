from kivy.graphics import InstructionGroup, Color, Ellipse

from score.notes import Note, dot_radius, dot_spacing


def update_dot_pos(dots: list[Ellipse], head: Note):
    pos = [head.x + head.dot_offset_x, head.y + head.dot_offset_y]
    for n, dot in enumerate(dots):
        dot.pos = [pos[0] - dot_radius, pos[1] - dot_radius]
        dot.size = [dot_radius * 2, dot_radius * 2]
        dot.flag_update()
        pos[0] += dot_spacing


def draw_dots(amount: int, head: Note):
    ret = InstructionGroup()
    ret.add(Color(rgba=(0, 0, 0, 1)))
    dots = []
    for n in range(amount):
        dot = Ellipse()
        ret.add(dot)
        dots.append(dot)
    head.bind(pos=lambda _, _2: update_dot_pos(dots, head),
              dot_offset=lambda _, _2: update_dot_pos(dots, head))
    update_dot_pos(dots, head)
    return ret
