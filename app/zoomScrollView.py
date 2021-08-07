from typing import Type

from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import Scatter as KvScatter
from kivy.uix.scrollview import ScrollView as KvScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget


class Scroll(KvScrollView):
    pass


class Scatter(KvScatter):
    pass





class ZoomScrollView(RelativeLayout, StencilView):
    scroll: Scroll
    scroll_dummy_widget: Widget
    scatter: Scatter
    widget: Type[Widget]

    zoom: int = NumericProperty()


    def __init__(self, widget, scroll_kwargs=None, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        StencilView.__init__(self, **kwargs)

        self.widget = widget

        if scroll_kwargs is None:
            scroll_kwargs = {}

        self.scroll = Scroll(do_scroll_x=True, do_scroll_y=True, scroll_type=["bars"], **scroll_kwargs)
        self.scatter = Scatter(auto_bring_to_front=False)
        self.scroll_dummy_widget = Widget()

        self.scroll.add_widget(self.scroll_dummy_widget)
        self.scatter.add_widget(self.widget)



        RelativeLayout.add_widget(self, self.scatter)
        RelativeLayout.add_widget(self, self.scroll)


    def add_widget(self, widget, index=0, canvas=None):
        raise Exception("You can only have one widget in ZoomScrollView")

    def on_zoom(self, _instance, value):
        self.scroll_dummy_widget.size = self.widget.size
        print(self.scroll_dummy_widget.pos, self.scroll_dummy_widget.size, self.scroll.size)

    def on_scroll_move(self, _instance, _value):
        self.scatter.pos = self.scroll.scroll_x, self.scroll.scroll_y
