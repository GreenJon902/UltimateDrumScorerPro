import math
from random import Random
from typing import Optional, Union

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.graphics import Line
from kivy.lang import Builder



class PosGetter:
    def __init__(self,
                 anchor_widget: Optional[EventDispatcher],
                 attr: Optional[Union[str, tuple[str, str]]],
                 offset: tuple[float, float],
                 distance_multiplier: float,
                 distance_offset: float,
                 random_distance: float,
                 random_perpendicular_distance: float,

                 random: Random,
                 random_step: float = 0.01):
        self.components = (
            offset,
            (anchor_widget, ((attr, attr) if isinstance(attr, str) else attr))
                if (anchor_widget is not None and attr is not None) else None,
            distance_multiplier,
            distance_offset,
            random_distance,
            random_perpendicular_distance
        )
        self.random = random
        self.random_step = random_step

    def get(self, other_point: tuple[float, float]):
        components = self.components

        pos = list(components[0])  # List so modifiable
        if components[1] is not None:
            pos[0] += getattr(components[1][0], components[1][1][0])
            pos[1] += getattr(components[1][0], components[1][1][1])
        if components[2] != 0 or components[3] != 0 or components[4] != 0 or components[5] != 0:
            distance = math.sqrt((other_point[0] - pos[0]) ** 2 + (other_point[1] - pos[1]) ** 2)
            angle = math.atan2(other_point[0] - pos[0], other_point[1] - pos[1])
            pos[0] += math.sin(angle) * distance * components[2]
            pos[1] += math.cos(angle) * distance * components[2]
            pos[0] += math.sin(angle) * components[3]
            pos[1] += math.cos(angle) * components[3]
            if components[4] != 0:
                a = int(components[4] / self.random_step)
                pos[0] += math.sin(angle) * self.random.randrange(-a, a, 1) * self.random_step
                pos[1] += math.cos(angle) * self.random.randrange(-a, a, 1) * self.random_step
            if components[5] != 0:
                b = int(components[5] / self.random_step)
                angle += math.radians(90)
                pos[0] += math.sin(angle) * self.random.randrange(-b, b, 1) * self.random_step
                pos[1] += math.cos(angle) * self.random.randrange(-b, b, 1) * self.random_step

        return pos


    def get_correct(self):
        components = self.components

        pos = list(components[0])  # List so modifiable
        if components[1] is not None:
            pos[0] += getattr(components[1][0], components[1][1][0])
            pos[1] += getattr(components[1][0], components[1][1][1])

        return pos


def update_points(line: Line, start_pos_getter, end_pos_getter):
    line.points = \
        *start_pos_getter.get(end_pos_getter.get_correct()), \
        *end_pos_getter.get(start_pos_getter.get_correct())
    line.flag_update()


def betterLine(
        start_anchor_widget: Optional[EventDispatcher], start_attr: Optional[Union[str, tuple[str, str]]],
        start_offset: tuple[float, float], start_distance_multiplier: float, start_distance_offset: float,
        start_random_distance: float, start_random_perpendicular_distance: float,
        end_anchor_widget: Optional[EventDispatcher], end_attr: Optional[Union[str, tuple[str, str]]],
        end_offset: tuple[float, float], end_distance_multiplier: float, end_distance_offset: float,
        end_random_distance: float, end_random_perpendicular_distance: float,
        width: float
):

    start_pos_getter = PosGetter(start_anchor_widget, start_attr, start_offset, start_distance_multiplier,
                                 start_distance_offset, start_random_distance, start_random_perpendicular_distance,
                                 Random())
    end_pos_getter = PosGetter(end_anchor_widget, end_attr, end_offset, end_distance_multiplier,
                               end_distance_offset, end_random_distance, end_random_perpendicular_distance,
                               Random())

    line = Line(width=width)  # We will get the points updated
    update_trigger = Clock.create_trigger(
        lambda *args, line_=line, start_pos_getter_=start_pos_getter, end_pos_getter_=end_pos_getter:
            update_points(line_, start_pos_getter_, end_pos_getter_), -1)

    if start_anchor_widget is not None and start_attr is not None:
        if isinstance(start_attr, str):
            start_anchor_widget.bind(**{start_attr: update_trigger})
        else:
            start_anchor_widget.bind(**{start_attr[0]: update_trigger, start_attr[1]: update_trigger})
    if end_anchor_widget is not None and end_attr is not None:
        if isinstance(start_attr, str):
            end_anchor_widget.bind(**{end_attr: update_trigger})
        else:
            end_anchor_widget.bind(**{end_attr[0]: update_trigger, end_attr[1]: update_trigger})

    update_trigger()

    return line


if __name__ == '__main__':
    import kivy.base
    from kivy.graphics import Color
    from kivy import metrics

    pos1 = (100, 300)
    pos2 = (500, 300)

    fl = Builder.load_string(f"""
FloatLayout:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: 0, 0, 0, 0.2
        Line:
            points: {pos1[0], pos1[1] + 10, pos2[0], pos2[1] + 10}
            width: mm(0.5)
""")
    with fl.canvas:
        Color(rgba=(0, 0, 0, 1))
        betterLine(None, None, pos1, 0.1, 0, 0, 10, None, None, pos2, 0, 10, 100, 0, metrics.mm(0.5))

    kivy.base.runTouchApp(fl)
