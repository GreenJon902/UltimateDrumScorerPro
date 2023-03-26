import kivy.base
from kivy import metrics
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterPlaneLayout
from kivy.uix.stacklayout import StackLayout

from assembler.pageContent.scoreSection import ScoreSection
from score import ScoreSectionStorage, ScoreSectionSectionStorage

max_note_id = 5


Builder.load_string("""
<ScoreSection>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: -2, -2
            size: self.width + 4, self.height + 4
""")


scoreSections1 = list()
for note1 in range(max_note_id + 1):
    for note2 in range(max_note_id + 1):
        scoreSections1.append(ScoreSection(None, score=ScoreSectionStorage([
            ScoreSectionSectionStorage(note_ids=[note1, note2]),
        ])))
scoreSections2 = list()
for note1 in range(max_note_id + 1):
    for note2 in range(max_note_id + 1):
        scoreSections2.append(ScoreSection(None, score=ScoreSectionStorage([
            ScoreSectionSectionStorage(note_ids=[note1]),
            ScoreSectionSectionStorage(note_ids=[note2]),
        ])))


container1 = StackLayout(spacing=5)
for scoreSection in scoreSections1:
    container1.add_widget(scoreSection)
container2 = StackLayout(spacing=5)
for scoreSection in scoreSections2:
    container2.add_widget(scoreSection)
container = BoxLayout(spacing=10, size=(210, 210))
container.add_widget(container1)
container.add_widget(container2)

root = ScatterPlaneLayout(scale=(metrics.mm(210) / 210))  # 210 is what we use in a normal page
root.add_widget(container)

kivy.base.runTouchApp(root)
