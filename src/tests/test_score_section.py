import typing

from kivy import metrics
from kivy.graphics import Instruction
from kivy.lang import Builder
from kivy.tests.common import GraphicUnitTest
from kivy.uix.scatter import ScatterPlane
from kivy.uix.widget import Widget

from renderer.scoreSection.scoreSection_normalBarCreator import ScoreSection_NormalBarCreator
from renderer.scoreSection.scoreSection_normalDotCreator import ScoreSection_NormalDotCreator
from renderer.scoreSection.scoreSection_opacityHeadCreator import ScoreSection_OpacityHeadCreator


class ScoreSectionTestCases(GraphicUnitTest):
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


    def scatter_render(self, func: typing.Callable[[], tuple[Instruction, float, float]]):
        design_holder = Widget(size_hint=(None, None))
        g, w, h = func()
        print(f"Size: {w, h}")
        design_holder.canvas.add(g)
        design_holder.canvas.flag_update()
        design_holder.size = w, h

        root = ScatterPlane(scale=(metrics.mm(1)))
        root.pos = 0, 0
        root.add_widget(design_holder)

        self.render(root)

    def test_bars(self):
        self.scatter_render(lambda: ScoreSection_NormalBarCreator((0, 0, 0, 1)).create(7, 5, 8))

    def test_dots(self):
        self.scatter_render(lambda: ScoreSection_NormalDotCreator((0, 0, 0, 1)).create(7))

    def test_heads(self):
        self.scatter_render(lambda: ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0.2)).create([1], [0,1]))
