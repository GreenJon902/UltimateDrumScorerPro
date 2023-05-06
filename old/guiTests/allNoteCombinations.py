import kivy.base
from assembler.pageContent.scoreSection import ScoreSection
from kivy import metrics
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from score import ScoreSectionStorage, ScoreSectionSectionStorage
from score.notes import notes

min_note_id = 0
max_note_id = len(notes)
note_ids = range(min_note_id, max_note_id)

container1_spacing = 5
container2_spacing = 5


Builder.load_string("""
<ScoreSection>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: -2, -2
            size: self.width + 4, self.height + 4
""")


class MyBoxLayout(BoxLayout):  # Allow no touch events through
    def on_touch_down(self, touch):
        pass
    def on_touch_move(self, touch):
        pass
    def on_touch_up(self, touch):
        pass


scoreSections1 = list()
for note1 in note_ids:
    for note2 in note_ids:
        scoreSections1.append(ScoreSection(None, score=ScoreSectionStorage([
            ScoreSectionSectionStorage(note_ids=[note1, note2]),
        ])))
scoreSections2 = list()
for note1 in note_ids:
    for note2 in note_ids:
        scoreSections2.append(ScoreSection(None, score=ScoreSectionStorage([
            ScoreSectionSectionStorage(note_ids=[note1]),
            ScoreSectionSectionStorage(note_ids=[note2]),
        ])))


container1 = StackLayout(spacing=container1_spacing, size_hint_x=None)
container1.width = sum([notes[note_id]().width + container1_spacing for note_id in note_ids])
for scoreSection in scoreSections1:
    container1.add_widget(scoreSection)
container2 = StackLayout(spacing=container2_spacing, size_hint_x=None)
container2.width = (max([notes[note_id]().width for note_id in note_ids]) * 2 + container2_spacing) * len(note_ids)
for scoreSection in scoreSections2:
    container2.add_widget(scoreSection)
container = MyBoxLayout(spacing=10, size=(10000, 210))
container.add_widget(container1)
container.add_widget(container2)
container.add_widget(Widget())  # Spacer

root = ScatterPlane(scale=(metrics.mm(210) / 210))  # 210 is what we use in a normal page
root.add_widget(container)

kivy.base.runTouchApp(root)
