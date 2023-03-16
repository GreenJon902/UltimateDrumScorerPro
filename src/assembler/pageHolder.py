import math

from kivy import metrics
from kivy.clock import Clock
from kivy.graphics.transformation import Matrix
from kivy.input import MotionEvent
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterPlaneLayout, ScatterLayout

from assembler.page import Page


class PageHolder(RelativeLayout):
    page: Page
    scatter1: ScatterPlaneLayout  # For the user control of the page
    scatter2: ScatterLayout  # For the centering of the page
    trigger_scale = None
    _touches: list[MotionEvent]

    zoom: int = NumericProperty(defaultvalue=1)
    pan_mode: int = BooleanProperty(defaultvalue=True)


    def __init__(self, **kwargs):
        self.trigger_scale = Clock.create_trigger(self._trigger_scale, -1)
        self.page = Page()
        self.scatter1 = ScatterPlaneLayout(do_translation=False, do_rotation=False, do_scale=False)
        self.scatter2 = ScatterLayout(do_translation=False, do_rotation=False, do_scale=False)
        self._touches = list()

        RelativeLayout.__init__(self, **kwargs)

        self.trigger_scale()
        self.scatter2.add_widget(self.page)
        self.scatter2.set_center_x(self.page.width / 2)
        self.scatter2.set_center_y(0)
        self.scatter1.add_widget(self.scatter2)
        self.add_widget(self.scatter1)

        self.bind(size=self.trigger_scale, zoom=self.trigger_scale)


    def _trigger_scale(self, _):
        self.scatter1.scale = (metrics.mm(self.page.width) / self.page.width) * self.zoom

    def on_touch_down(self, touch: MotionEvent):
        if self.pan_mode:
            touch.grab(self)
            self._touches.append(touch)
            return True
        return RelativeLayout.on_touch_down(self, touch)

    def on_touch_move(self, touch: MotionEvent):
        if touch.grab_current == self:
            self.transform_with_touch(touch)
            return True

        return RelativeLayout.on_touch_down(self, touch)

    def on_touch_up(self, touch: MotionEvent):
        if touch.grab_current == self:
            touch.ungrab(self)
            self._touches.remove(touch)
            return True
        return RelativeLayout.on_touch_down(self, touch)


    def transform_with_touch(self, touch: MotionEvent):
        if len(self._touches) == 1:  # Transformation
            self.scatter1.apply_transform(Matrix().translate(touch.dx, touch.dy, 0))

        if len(self._touches) == 2 and False:  # Zoom  TODO: Make this not so angry
            other_touch = self._touches[1] if self._touches[0] == touch else self._touches[0]
            before = math.sqrt((other_touch.x - touch.ox) ** 2 + (other_touch.y - touch.oy) ** 2)
            after = math.sqrt((other_touch.x - touch.x) ** 2 + (other_touch.y - touch.y) ** 2)
            change = after / before
            self.scatter1.apply_transform(Matrix().scale(change, change, change), anchor=other_touch.pos)
