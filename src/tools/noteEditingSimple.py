import os

from kivy import metrics
from kivy.lang import Builder
from kivy.uix.scatter import ScatterPlane

from renderer.scoreSection import ScoreSectionRenderer
from renderer.scoreSection.scoreSection_normalBarCreator import ScoreSection_NormalBarCreator
from renderer.scoreSection.scoreSection_normalComponentOrganiser import ScoreSection_NormalComponentOrganiser
from renderer.scoreSection.scoreSection_normalDecorationCreator import ScoreSection_NormalDecorationCreator
from renderer.scoreSection.scoreSection_normalDotCreator import ScoreSection_NormalDotCreator
from renderer.scoreSection.scoreSection_normalNoteHeightCalculator import ScoreSection_NormalNoteHeightCalculator
from renderer.scoreSection.scoreSection_normalStemCreator import ScoreSection_NormalStemCreator
from renderer.scoreSection.scoreSection_opacityHeadCreator import ScoreSection_OpacityHeadCreator
from scoreStorage.scoreSectionStorage import ScoreSectionSectionStorage, ScoreSectionStorage

os.environ["KCFG_INPUT_MOUSE"] = "mouse,multitouch_on_demand"

import kivy.base
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


Builder.load_string("""
<ScoreSectionRenderer>:
    canvas.before:
        Color:
            rgba: 0.7, 0.7, 0.7, 1
        Rectangle:
            pos: -1000, -1000
            size: self.width + 2000, self.height + 2000
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: -2, -2
            size: self.width + 4, self.height + 4
""")


n = 0
start_location = 0


scoreSectionStorage = ScoreSectionStorage()


def update(_):
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
    else:
        print("No more changes to make!!")
    n += 1


for n in range(start_location + 1):
    update(n)


renderer = ScoreSectionRenderer(scoreSectionStorage, bar_creator=ScoreSection_NormalBarCreator((0, 0, 0, 1)),
                                dot_creator=ScoreSection_NormalDotCreator((0, 0, 0, 1)),
                                head_creator=ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0)),
                                component_organiser=ScoreSection_NormalComponentOrganiser(),
                                stem_creator=ScoreSection_NormalStemCreator((0, 0, 0, 1)),
                                decoration_creator=ScoreSection_NormalDecorationCreator((0, 0, 0, 1)),
                                note_height_calculator=ScoreSection_NormalNoteHeightCalculator())


root = ScatterPlane(scale=(metrics.mm(210) / 210))  # 210 is what we use in a normal page
root.add_widget(renderer)

boxLayout = BoxLayout(orientation="vertical")
boxLayout.add_widget(root)
boxLayout.add_widget(Button(text="next", on_release=update, size_hint_y=0.2))


kivy.base.runTouchApp(boxLayout)
