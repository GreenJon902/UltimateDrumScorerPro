from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from app.graphicsConstants import page_bg_color, page_with_to_height_ratio


class ScoreViewException(Exception):
    pass


class PageHolder(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None


    def add_page(self, widget):
        if not isinstance(widget, Page):
            raise ScoreViewException(f"PageHolder only accepts Page widget, not {widget.__class__}")

        return BoxLayout.add_widget(self, widget, len(self.children))


    def on_children(self, _instance, value):
        self.height = self.width * page_with_to_height_ratio * len(value)

    def on_width(self, _instance, value):
        self.height = value * page_with_to_height_ratio * len(self.children)


class Page(RelativeLayout):
    draw: callable

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.size_hint_y = None

        self.draw = Clock.create_trigger(lambda _elapsed_time: self._draw())
        self.bind(pos=self.draw, size=self.draw)


    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(rgb=page_bg_color)
            Rectangle(pos=self.pos, size=self.size)

            Color(rgb=(1, 0, 0))
            Rectangle(pos=(self.x - 5, self.top - 5), size=(10, 10))
            Rectangle(pos=(self.x - 5, self.y - 5), size=(10, 10))
            Rectangle(pos=(self.right - 5, self.top - 5), size=(10, 10))
            Rectangle(pos=(self.right - 5, self.y - 5), size=(10, 10))

    def on_width(self, _instance, value):
        self.height = value * page_with_to_height_ratio



class ScoreView(RelativeLayout):
    zoom = NumericProperty(1)
    scrollView: ScrollView
    pageHolder: PageHolder

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.scrollView = ScrollView(size_hint_x=None, size_hint_y=1, pos_hint={"center_x": 0.5})
        self.pageHolder = PageHolder()

        self.pageHolder.add_page(Page())

        self.scrollView.add_widget(self.pageHolder)
        self.add_widget(self.scrollView)


    def on_zoom(self, _instance, value):
        self.scrollView.width = self.width * value

    def on_width(self, _instance, value):
        self.scrollView.width = value * self.zoom
