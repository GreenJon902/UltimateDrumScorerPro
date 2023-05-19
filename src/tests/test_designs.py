from kivy import metrics
from kivy.lang import Builder
from kivy.metrics import mm
from kivy.tests.common import GraphicUnitTest
from kivy.uix.scatter import ScatterPlane
from kivy.uix.widget import Widget

from scoreSectionDesigns.notes import check_notes, notes

check_notes()


class DesignRenderingTestCases(GraphicUnitTest):
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


    def scatter_render(self, design):
        design_holder = Widget(size_hint=(None, None))
        with design_holder.canvas:
            design.draw()

        root = ScatterPlane(scale=(metrics.mm(10) / 10), size=(mm(10), mm(10)), size_hint=(None, None))
        root.pos = 0, 0
        root.add_widget(design_holder)

        self.render(root)


for nid in notes:
    note = notes[nid]
    name = note.name.lower()
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    setattr(DesignRenderingTestCases, f"test_{name}",
            lambda self: DesignRenderingTestCases.scatter_render(self, note))

