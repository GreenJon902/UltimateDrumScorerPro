from kivy import metrics
from kivy.clock import Clock
from kivy.graphics.transformation import Matrix
from kivy.input import MotionEvent
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterPlaneLayout, ScatterLayout

from assembler.page import Page


class PageHolder(RelativeLayout):
    page: Page
    userControlHolder: ScatterPlaneLayout  # For the user control of the page
    centerHolder: FloatLayout  # For the centering of the page
    generalHolder: FloatLayout  # So center holder can be moved around
    trigger_scale = None
    _touches: list[MotionEvent]

    zoom: float = NumericProperty(defaultvalue=1)

    def __init__(self, contents=None, **kwargs):
        self.trigger_scale = Clock.create_trigger(self._trigger_scale, -1)
        self.page = Page(contents)
        self.userControlHolder = ScatterLayout(do_translation=False, do_rotation=False, do_scale=False,
                                               do_collide_after_children=True, size_hint=(None, None))
        self.centerHolder = RelativeLayout()
        self.generalHolder = FloatLayout()
        self._touches = list()

        RelativeLayout.__init__(self, **kwargs)

        self.userControlHolder.add_widget(self.page)
        self.centerHolder.add_widget(self.userControlHolder)
        self.generalHolder.add_widget(self.centerHolder)
        self.add_widget(self.generalHolder)

        self.userControlHolder.size = self.page.size
        self.userControlHolder.center = 0, 0
        self.trigger_scale()

        self.bind(size=self.trigger_scale, zoom=self.trigger_scale)

    def _trigger_scale(self, _):
        self.userControlHolder.scale = (metrics.mm(self.page.width) / self.page.width) * self.zoom
        self.centerHolder.pos = self.width / 2, self.height / 2

    def on_touch_down(self, touch: MotionEvent):
        ret = RelativeLayout.on_touch_down(self, touch)
        if not ret and self.collide_point(touch.x, touch.y):
            self._touches.append(touch)
            touch.grab(self)
            ret = True
        return ret

    def on_touch_move(self, touch: MotionEvent):
        if touch.grab_current == self:
            self.userControlHolder.apply_transform(Matrix().translate(touch.dx, touch.dy, 0))
            return True

        return RelativeLayout.on_touch_down(self, touch)  # Have this last as scatter always returns true

    def on_touch_up(self, touch: MotionEvent):
        ret = RelativeLayout.on_touch_up(self, touch)
        if not ret and touch.grab_current == self:
            touch.ungrab(self)
            self._touches.remove(touch)
            ret = True
        return ret
