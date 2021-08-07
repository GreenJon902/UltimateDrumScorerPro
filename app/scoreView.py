from kivy import app
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, MatrixInstruction, Scale
from kivy.graphics.transformation import Matrix
from kivy.properties import NumericProperty, DictProperty, ReferenceListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

import scoreContent
from app.graphicsConstants import page_bg_color, page_with_to_height_ratio, scroll_bar_color, scroll_bar_inactive_color, \
    scroll_bar_width, page_size
from app.zoomScrollView import ZoomScrollView


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




class PageBg(Widget):
    def __init__(self, **kwargs):
        Widget.__init__(self, **kwargs)
        self.size_hint = None, None
        self.size = page_size




class PageContent(RelativeLayout):
    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.size_hint = None, None
        self.size = page_size




class Page(RelativeLayout):
    page_bg: PageBg
    content: PageContent

    scale_x: int = NumericProperty(1)
    scale_y: int = NumericProperty(1)
    scale_z: int = NumericProperty(1)
    scale_xyz: tuple[int, int, int] = ReferenceListProperty(scale_x, scale_y, scale_z)

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.size_hint_y = None

        self.content = PageContent()

        self.page_bg = PageBg()
        self.add_widget(self.page_bg)
        self.add_widget(self.content)


        self.scale_instruction = Scale(matrix=Matrix())



    def on_width(self, _instance, value):
        self.height = value * page_with_to_height_ratio


    def on_touch_down(self, touch):
        current_click_mode = App.get_running_app().sidebar_button_current.name \
            if App.get_running_app().sidebar_button_current is not None else None

        x, y = self.get_pos_hint_from_pos(*touch.pos)
        location_to_put = {"center_x": x, "center_y": y}
        del x, y

        if current_click_mode == "add_text":
            App.get_running_app().discard_click_mode()

            content = scoreContent.Text(location_to_put)
            self.content.add_widget(content)



    def get_pos_hint_from_pos(self, x, y):
        rx, ry = RelativeLayout.to_local(self, x, y)

        hx = rx / self.width
        hy = ry / self.height

        print(hx, rx, self.width, hy, ry, self.height)

        return hx, hy

    def on_size(self, _instance, _value):
        dmx = self.width / page_size[0]
        dmy = self.height / page_size[1]
        dmz = 1

        self.scale_xyz = dmx, dmy, dmz



class ScoreView(RelativeLayout):
    zoom = NumericProperty(1)
    scrollView: ScrollView
    pageHolderHolder: RelativeLayout
    pageHolder: PageHolder

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.scrollView = ScrollView(do_scroll_x=True, do_scroll_y=True, scroll_type=["bars"],
                                     bar_width=scroll_bar_width, bar_color=scroll_bar_color,
                                     bar_inactive_color=scroll_bar_inactive_color)
        self.pageHolderHolder = RelativeLayout(size_hint_y=None, size_hint_x=None)
        self.pageHolder = PageHolder(size_hint_x=None, size_hint_y=None, pos_hint={"center_x": 0.5})

        self.pageHolder.add_page(Page())


        self.pageHolder.bind(height=lambda _instance, value: set_height(self.pageHolderHolder, value))

        self.pageHolderHolder.add_widget(self.pageHolder)
        self.scrollView.add_widget(self.pageHolderHolder)
        self.add_widget(self.scrollView)


    def on_zoom(self, _instance, value):
        self.pageHolder.width = self.width * value
        self.do_page_holder_holder_size()
        self.scrollView.zoom = value

    def on_width(self, _instance, value):
        self.pageHolder.width = value * self.zoom
        self.do_page_holder_holder_size()

    def do_page_holder_holder_size(self):
        if self.pageHolder.width > self.width:
            self.pageHolderHolder.width = self.pageHolder.width

        else:
            self.pageHolderHolder.width = self.width



def set_height(widget, value):
    widget.height = value


def focus_text_input(box):
    box.focus = True


