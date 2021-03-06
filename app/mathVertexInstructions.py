from kivy.clock import Clock
from kivy.graphics import Line, Ellipse, Rectangle


class MathLine(Line):
    redo_maths: callable

    def __init__(self, instance, properties_to_bind, points, **kwargs):
        self.point_strings = points
        self.instance = instance

        self.redo_maths = Clock.create_trigger(lambda _elapsed_time: self._redo_maths(), -1)

        self.redo_maths()
        Line.__init__(self, **kwargs)

        for property_to_bind in properties_to_bind:
            self.instance.fbind(property_to_bind, lambda _instance, _value: self.redo_maths())


    def _redo_maths(self):
        points = list()

        for point_str in self.point_strings:
            points.append(eval(point_str, {}, {"self": self.instance}))

        self.points = points


class MathEllipse(Ellipse):
    redo_maths: callable

    def __init__(self, instance, properties_to_bind, pos, **kwargs):
        self.pos_string = pos
        self.instance = instance

        self.redo_maths = Clock.create_trigger(lambda _elapsed_time: self._redo_maths(), -1)

        self.redo_maths()
        Ellipse.__init__(self, **kwargs)

        for property_to_bind in properties_to_bind:
            self.instance.fbind(property_to_bind, lambda _instance, _value: self.redo_maths())


    def _redo_maths(self):
        pos = list()

        for coord_str in self.pos_string:
            pos.append(eval(coord_str, {}, {"self": self.instance}))

        self.pos = pos



class MathRectangle(Rectangle):
    redo_maths: callable

    def __init__(self, instance, properties_to_bind, pos, **kwargs):
        self.pos_string = pos
        self.instance = instance

        self.redo_maths = Clock.create_trigger(lambda _elapsed_time: self._redo_maths(), -1)

        self.redo_maths()
        Rectangle.__init__(self, **kwargs)

        for property_to_bind in properties_to_bind:
            self.instance.fbind(property_to_bind, lambda _instance, _value: self.redo_maths())


    def _redo_maths(self):
        pos = list()

        for coord_str in self.pos_string:
            pos.append(eval(coord_str, {}, {"self": self.instance}))

        self.pos = pos
