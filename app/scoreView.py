from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

from app.graphicsConstants import page_bg_color


class ScoreViewException(Exception):
    pass




class ScoreView(ScrollView):
    def __init__(self, **kwargs):
        ScrollView.__init__(self, **kwargs)

        self.add_widget(PageHolder())


class PageHolder(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        self.add_widget(Page())

    def add_widget(self, widget, index=0, canvas=None):
        if not isinstance(widget, Page):
            raise ScoreViewException(f"PageHolder only accepts Page widget, not {widget.__class__}")

        return BoxLayout.add_widget(self, widget, index, canvas)




class Page(RelativeLayout):
    draw: callable

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.draw = Clock.create_trigger(lambda _elapsed_time: self._draw())
        self.bind(pos=self.draw, size=self.draw)


    def _draw(self):
        with self.canvas.before:
            Color(rgb=page_bg_color)
            Rectangle(pos=self.pos, size=self.size)


