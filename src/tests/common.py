from kivy import metrics
from kivy.lang import Builder
from kivy.tests.common import GraphicUnitTest as KivyGraphicUnitTest
from kivy.uix.scatter import ScatterPlane
from kivy.uix.widget import Widget


def gen_parameter_combo(possibilities):
    a = possibilities[0]
    ret = []

    for b in a:
        if len(possibilities) == 1:
            ret.append([b])
        else:
            for p in gen_parameter_combo(possibilities[1:]):
                ret.append([b] + p)

    return ret


class GraphicUnitTest(KivyGraphicUnitTest):
    @classmethod
    def setUpClass(cls) -> None:
        Builder.load_string("""
<ScatterPlane>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: -2, -2
            size: self.width + 4, self.height + 4
        """)


    def scatter_render(self, g, w, h):
        design_holder = Widget(size_hint=(None, None))
        design_holder.canvas.add(g)
        design_holder.canvas.flag_update()
        design_holder.size = w, h

        root = ScatterPlane(scale=(metrics.mm(1)))
        root.pos = 0, 0
        root.add_widget(design_holder)

        self.render(root)


__all__ = ["GraphicUnitTest"]
