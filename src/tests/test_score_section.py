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

n = 0
def update(scoreSectionStorage):  # Returns True while there are more steps, returns False if nothing else
    global n
    print(n)
    if n == 0:  # Heads and stems
        scoreSectionStorage.set([ScoreSectionSectionStorage(note_ids=[0, 1, 2, 4]),
                                 ScoreSectionSectionStorage(note_ids=[0, 2, 4])])
    elif n == 1:
        scoreSectionStorage.append(ScoreSectionSectionStorage(note_ids=[5]))
    elif n == 2:
        scoreSectionStorage.insert(1, ScoreSectionSectionStorage(note_ids=[2]))
    elif n == 3:
        scoreSectionStorage[0].note_ids.remove(1)
    elif n == 4:
        scoreSectionStorage[1].note_ids = [0, 1, 2, 3, 4, 5]
    elif n == 5:  # Bars
        scoreSectionStorage.set([
            ScoreSectionSectionStorage(note_ids=[0]),
            ScoreSectionSectionStorage(note_ids=[0]),
            ScoreSectionSectionStorage(note_ids=[0], bars=1),
            ScoreSectionSectionStorage(note_ids=[0], bars=2),
            ScoreSectionSectionStorage(note_ids=[0]),
            ScoreSectionSectionStorage(note_ids=[0], bars=1, before_flags=1),
            ScoreSectionSectionStorage(note_ids=[0], bars=1, after_flags=1),
            ScoreSectionSectionStorage(slanted_flags=2),
        ])
    elif n == 6:
        scoreSectionStorage[1].note_ids.append(1)
    elif n == 7:
        scoreSectionStorage[5].bars = 3
        scoreSectionStorage[3].bars -= 1
        scoreSectionStorage[6].bars -= 1
    elif n == 8:
        scoreSectionStorage[1].before_flags = 10
        scoreSectionStorage[1].after_flags = 10
        scoreSectionStorage[-1].slanted_flags = 10
    elif n == 9:  # Dots
        scoreSectionStorage.dots_at_top = True
        scoreSectionStorage.set([ScoreSectionSectionStorage(note_ids=[0], dots=10)])
    elif n == 10:
        scoreSectionStorage.set([ScoreSectionSectionStorage(note_ids=[0], dots=1),
                                 ScoreSectionSectionStorage(note_ids=[0], bars=1, dots=2)])
    elif n == 11:
        scoreSectionStorage.insert(1, ScoreSectionSectionStorage(note_ids=[0], dots=5))
    elif n == 12:
        scoreSectionStorage[1].dots = 1
    elif n == 13:
        scoreSectionStorage[1].dots = 0
    elif n == 14:
        scoreSectionStorage[0].dots = 0
        scoreSectionStorage[2].dots = 0
    elif n == 15:  # Removing sections
        scoreSectionStorage.set([ScoreSectionSectionStorage(note_ids=[0]),
                                 ScoreSectionSectionStorage(note_ids=[0], bars=1, dots=1),
                                 ScoreSectionSectionStorage(note_ids=[0], bars=2, after_flags=1)])
    elif n == 16:
        scoreSectionStorage.pop()
    elif n == 17:
        scoreSectionStorage.pop(1)
    elif n == 18:
        scoreSectionStorage.set([ScoreSectionSectionStorage(note_ids=[0]),
                                 ScoreSectionSectionStorage(note_ids=[0], bars=1, dots=1),
                                 ScoreSectionSectionStorage(note_ids=[0], bars=2, after_flags=1)])
    elif n == 19:
        scoreSectionStorage.remove(scoreSectionStorage[0])
    elif n == 20:
        scoreSectionStorage.set([ScoreSectionSectionStorage(decoration_id=0)])
    elif n == 21:
        scoreSectionStorage.insert(0, ScoreSectionSectionStorage(note_ids=[0]))
    elif n == 22:
        scoreSectionStorage[1].note_ids = [0, 1, 2]
    elif n == 23:
        scoreSectionStorage[1].decoration_id = 4
    else:
        print("No more changes to make!!")
        return False
    n += 1
    return True


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
        storage = ScoreSectionStorage([])

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

        while update(storage):
            self.render(renderer)


__all__ = ["ScoreSectionTestCases"]
