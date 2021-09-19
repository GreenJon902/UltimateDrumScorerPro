from kivy.clock import Clock
from kivy.graphics import Line


class BetterLine(Line):
    redo_maths: callable

    def __init__(self, bar_instance, properties_to_bind, points, **kwargs):
        self.point_strings = points
        self.bar_instance = bar_instance

        self.redo_maths = Clock.create_trigger(lambda _elapsed_time: self._redo_maths())

        self.redo_maths()
        Line.__init__(self, **kwargs)

        for property_to_bind in properties_to_bind:
            self.bar_instance.fbind(property_to_bind, lambda _instance, _value: self.redo_maths())


    def _redo_maths(self):
        points = list()

        for point_str in self.point_strings:
            points.append(eval(point_str, {}, {"self": self.bar_instance}))

        self.points = points
