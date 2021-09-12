from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

import constants
from app.uix.scoreViewHelpers import set_height
from app.uix.scoreViewHelpers.page import PageHolder, Page
from logger import ClassWithLogger


class ScoreView(RelativeLayout, ClassWithLogger):
    zoom = NumericProperty(1)
    scrollView: ScrollView
    pageHolderHolder: RelativeLayout
    pageHolder: PageHolder

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.scrollView = ScrollView(do_scroll_x=True, do_scroll_y=True, scroll_type=["bars"],
                                     bar_width=constants.graphics.scroll_bar_width,
                                     bar_color=constants.graphics.scroll_bar_color,
                                     bar_inactive_color=constants.graphics.scroll_bar_inactive_color)
        self.pageHolderHolder = RelativeLayout(size_hint_y=None, size_hint_x=None)
        self.pageHolder = PageHolder(size_hint_x=None, size_hint_y=None, pos_hint={"center_x": 0.5})

        page = Page()
        self.pageHolder.add_page(page)

        self.pageHolder.bind(height=lambda _instance, value: set_height(self.pageHolderHolder, value))

        self.pageHolderHolder.add_widget(self.pageHolder)
        self.scrollView.add_widget(self.pageHolderHolder)
        self.add_widget(self.scrollView)


    def on_zoom(self, _instance, value):
        self.pageHolder.width = self.width * value
        self.do_page_holder_holder_size()

    def on_width(self, _instance, value):
        self.pageHolder.width = value * self.zoom
        self.do_page_holder_holder_size()

    def do_page_holder_holder_size(self):
        if self.pageHolder.width > self.width:
            self.pageHolderHolder.width = self.pageHolder.width

        else:
            self.pageHolderHolder.width = self.width


    def set_scroll_view_scroll_mode(self, thing: list[str]):
        self.log_dump(f"Setting scroll_view.scroll_type too {thing}")
        self.scrollView.scroll_type = thing
