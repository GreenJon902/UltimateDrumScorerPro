import typing

from kivy.graphics import Instruction
from parameterized import parameterized

from renderer.scoreSection import ScoreSectionRenderer
from renderer.scoreSection.scoreSection_normalBarCreator import ScoreSection_NormalBarCreator
from renderer.scoreSection.scoreSection_normalComponentOrganiser import ScoreSection_NormalComponentOrganiser
from renderer.scoreSection.scoreSection_normalDotCreator import ScoreSection_NormalDotCreator
from renderer.scoreSection.scoreSection_normalNoteHeightCalculator import ScoreSection_NormalNoteHeightCalculator
from renderer.scoreSection.scoreSection_opacityHeadCreator import ScoreSection_OpacityHeadCreator
from scoreStorage.scoreSectionStorage import ScoreSectionStorage, ScoreSectionSectionStorage
from tests.common import GraphicUnitTest, gen_parameter_combo


class ScoreSectionTestCases(GraphicUnitTest):
    def do(self, func: typing.Callable[[], tuple[Instruction, float, float]]):
        g, w, h, *_ = func()
        print(f"Size: {w, h}")
        self.scatter_render(g, w, h)

    def test_bars(self):
        self.do(lambda: ScoreSection_NormalBarCreator((0, 0, 0, 1)).create(None, 7, 5, 8, 6))

    def test_dots(self):
        self.do(lambda: ScoreSection_NormalDotCreator((0, 0, 0, 1)).create(None, 7))

    def test_heads(self):
        self.do(lambda: ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0.2)).create(None, [(1, 5), (2, 10)],
                                                                                             {0, 1}))

    @parameterized.expand([
        *gen_parameter_combo([
            [None, lambda: ScoreSection_NormalBarCreator((0, 0, 0, 1))],
            [None, lambda: ScoreSection_NormalDotCreator((0, 0, 0, 1))],
            [None, lambda: ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0)),
             lambda: ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0.5))],
            [lambda: ScoreSection_NormalComponentOrganiser()],
            [lambda: ScoreSection_NormalNoteHeightCalculator()]
        ])
    ])
    def test_whole(self, bar, dot, head, organiser, calculator):  # Just to demonstrate that any combination works
        storage = ScoreSectionStorage([
            ScoreSectionSectionStorage(note_ids=[2, 3]),
            ScoreSectionSectionStorage(note_ids=[5, 7, 1], before_flags=2, after_flags=3, bars=1),
            ScoreSectionSectionStorage(note_ids=[5, 6, 1], dots=3, bars=4),
            ScoreSectionSectionStorage(note_ids=[], slanted_flags=2)
        ])

        print(bar, dot, head, organiser, calculator)
        bar = bar() if bar is not None else None
        dot = dot() if dot is not None else None
        head = head() if head is not None else None
        organiser = organiser()
        calculator = calculator()
        print(bar, dot, head, organiser, calculator)

        renderer = ScoreSectionRenderer(storage, bar_creator=bar, dot_creator=dot, head_creator=head,
                                        component_organiser=organiser, note_height_calculator=calculator)
        print("=>", renderer)
        self.render(renderer)


__all__ = ["ScoreSectionTestCases"]
