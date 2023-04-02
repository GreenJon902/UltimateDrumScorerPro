import kivy.base
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from assembler import Assembler
from assembler.pageContent.scoreSection import ScoreSection
from editor import Editor
from score import ScoreSectionStorage, ScoreSectionSectionStorage

n = 0
start_location = 0


scoreSectionStorage = ScoreSectionStorage()


def update(_):
    global n
    if n == 0:
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
    n += 1


for n in range(start_location):
    update(n)

boxLayout = BoxLayout(orientation="vertical")
editor = Editor()
boxLayout.add_widget(Assembler(
    [
        [
            ScoreSection(editor, pos=(210 / 2, 297 / 2), score=scoreSectionStorage),
        ]
    ]
)
)
boxLayout.add_widget(editor)
boxLayout.add_widget(Button(text="next", on_release=update, size_hint_y=0.2))



kivy.base.runTouchApp(boxLayout)
