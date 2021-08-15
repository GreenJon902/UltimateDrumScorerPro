from kivy.graphics import Scale
from kivy.graphics.transformation import Matrix
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from app import metrics, scoreContent
from app.misc import check_mode
from app.scoreView.helperFunctions import ScoreViewException
from logger import ClassWithLogger


class PageHolder(BoxLayout, ClassWithLogger):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.orientation = "vertical"
        self.size_hint_y = None


    def add_page(self, widget):
        if not isinstance(widget, Page):
            raise ScoreViewException(f"PageHolder only accepts Page widget, not {widget.__class__}")

        self.log_debug("Adding Page")

        return BoxLayout.add_widget(self, widget, len(self.children))


    def on_children(self, _instance, value):
        self.height = metrics.Page.width_to_height(self.width) * len(value)

    def on_width(self, _instance, value):
        self.height = metrics.Page.width_to_height(value) * len(self.children)




class PageBg(Widget):
    def __init__(self, **kwargs):
        Widget.__init__(self, **kwargs)
        self.size_hint = None, None
        self.size = metrics.page_size_px




class PageContent(RelativeLayout):
    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.size_hint = None, None
        self.size = metrics.page_size_px




class Page(RelativeLayout, ClassWithLogger):
    page_bg: PageBg
    content: PageContent

    scale_x: int = NumericProperty(1)
    scale_y: int = NumericProperty(1)
    scale_z: int = NumericProperty(1)
    scale_xyz: tuple[int, int, int] = ReferenceListProperty(scale_x, scale_y, scale_z)

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.size_hint_y = None

        self.content = PageContent()

        self.page_bg = PageBg()
        self.add_widget(self.page_bg)
        self.add_widget(self.content)


        self.scale_instruction = Scale(matrix=Matrix())



    def on_width(self, _instance, value):
        self.height = metrics.Page.width_to_height(value)


    def on_touch_up(self, touch):
        if RelativeLayout.on_touch_up(self, touch):
            return True


        else:
            self.log_debug("Adding Content")

            if check_mode("text"):
                self.log_dump("which is text")

                content = scoreContent.Text(pos=self.to_local(*touch.pos))
                self.content.add_widget(content)


            elif check_mode("section"):
                self.log_dump("which is a section")

                content = scoreContent.Section(pos=self.to_local(*touch.pos))
                self.content.add_widget(content)


            elif check_mode("move"):
                self.log_debug("or not... Hand was selected")
                return False

            return True


    def to_local(self, px, py, **kwargs):
        lxh, lyh = self.get_pos_hint_from_pos(px, py)

        nx = lxh * metrics.page_size_px[0]
        ny = lyh * metrics.page_size_px[1]

        return nx, ny


    def to_parent(self, px, py, **kwargs):  # Might not be right, have no way to test
        lxh = px / metrics.page_size_px[0]
        lyh = py / metrics.page_size_px[1]

        nx = lxh * self.width
        ny = lyh * self.height

        return RelativeLayout.to_parent(self, nx, ny, **kwargs)



    def get_pos_hint_from_pos(self, x, y):
        rx, ry = RelativeLayout.to_local(self, x, y)

        hx = rx / self.width
        hy = ry / self.height

        return hx, hy

    def on_size(self, _instance, _value):
        dmx = self.width / metrics.page_size_px[0]
        dmy = self.height / metrics.page_size_px[1]
        dmz = 1

        self.scale_xyz = dmx, dmy, dmz