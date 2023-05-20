import typing

from kivy.graphics import Instruction
from parameterized import parameterized

from renderer.scoreSection import ScoreSectionRenderer
from renderer.scoreSection.scoreSection_normalBarCreator import ScoreSection_NormalBarCreator
from renderer.scoreSection.scoreSection_normalComponentOrganiser import ScoreSection_NormalComponentOrganiser
from renderer.scoreSection.scoreSection_normalDotCreator import ScoreSection_NormalDotCreator
from renderer.scoreSection.scoreSection_opacityHeadCreator import ScoreSection_OpacityHeadCreator
from scoreStorage.scoreSectionStorage import ScoreSectionStorage, ScoreSectionSectionStorage
from tests.common import GraphicUnitTest, gen_organiser_parameters_recur


class ScoreSectionTestCases(GraphicUnitTest):
    def do(self, func: typing.Callable[[], tuple[Instruction, float, float]]):
        g, w, h = func()
        print(f"Size: {w, h}")
        self.scatter_render(g, w, h)

    def test_bars(self):
        self.do(lambda: ScoreSection_NormalBarCreator((0, 0, 0, 1)).create(7, 5, 8))

    def test_dots(self):
        self.do(lambda: ScoreSection_NormalDotCreator((0, 0, 0, 1)).create(7))

    def test_heads(self):
        self.do(lambda: ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0.2)).create([1], [0, 1]))

    @parameterized.expand([
        *gen_organiser_parameters_recur([
            [None, ScoreSection_NormalBarCreator],
            [None, ScoreSection_NormalDotCreator],
            [None, lambda: ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0)),
             lambda: ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0.5))],
            [None, ScoreSection_NormalComponentOrganiser]
        ])
    ])
    def test_whole(self, bar, dot, head, organiser):  # Just to demonstrate that any combination works
        storage = ScoreSectionStorage([
            ScoreSectionSectionStorage(note_ids=[2, 3]),
            ScoreSectionSectionStorage(note_ids=[5, 7, 1], before_flags=2, after_flags=3, bars=1),
            ScoreSectionSectionStorage(note_ids=[5, 6, 1], dots=3, bars=4),
            ScoreSectionSectionStorage(note_ids=[], slanted_flags=2)
        ])
        print(bar, dot, head, organiser)
        renderer = ScoreSectionRenderer(storage, bar_creator=bar, dot_creator=dot, head_creator=head,
                                        component_organiser=organiser)
        print("=>", renderer)
        self.render(renderer)


__all__ = ["ScoreSectionTestCases"]
