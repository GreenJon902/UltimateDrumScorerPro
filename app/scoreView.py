from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

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
            Rectangle(pos=(0, 0), size=self.size)


    def on_width(self, _instance, value):
        self.height = value * page_with_to_height_ratio



class ScoreView(RelativeLayout):
    zoom = NumericProperty(1)
    scrollView: ScrollView
    pageHolderHolder: RelativeLayout
    pageHolder: PageHolder

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.scrollView = ScrollView()
        self.pageHolderHolder = RelativeLayout(size_hint_y=None)
        self.pageHolder = PageHolder(size_hint_x=None, size_hint_y=None, pos_hint={"center_x": 0.5})

        self.pageHolder.add_page(Page())


        self.pageHolder.bind(height=lambda _instance, value: set_height(self.pageHolderHolder, value))

        self.pageHolderHolder.add_widget(self.pageHolder)
        self.scrollView.add_widget(self.pageHolderHolder)
        self.add_widget(self.scrollView)


    def on_zoom(self, _instance, value):
        self.pageHolder.width = self.width * value

    def on_width(self, _instance, value):
        self.pageHolder.width = value * self.zoom



def set_height(widget, value):
    widget.height = value
