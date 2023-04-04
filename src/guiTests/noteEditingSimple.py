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
        scoreSectionStorage[1].slanted_flags = 10
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
    else:
        print("No more changes to make!!")
    n += 1


for n in range(start_location + 1):
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
