import kivy.base
from kivy import metrics
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget

from assembler.pageContent.scoreSection import ScoreSection
from score import ScoreSectionStorage, ScoreSectionSectionStorage
from score.decorations import decorations

min_decoration_id = 0
max_decoration_id = len(decorations)
decoration_ids = range(min_decoration_id, max_decoration_id)

container_spacing = 5


Builder.load_string("""
<BoxLayout>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: -2, -2
            size: self.size
""")


class MyBoxLayout(BoxLayout):  # Allow no touch events through
    def on_touch_down(self, touch):
        pass
    def on_touch_move(self, touch):
        pass
    def on_touch_up(self, touch):
        pass


scoreSections = list()
for decoration in decoration_ids:
    scoreSections.append(ScoreSection(None, score=ScoreSectionStorage([
        ScoreSectionSectionStorage(decoration_id=decoration),
    ])))


container = StackLayout(spacing=container_spacing, size_hint_x=None)
container.width = sum([decorations[decoration_id]().width + container_spacing for decoration_id in decoration_ids])
for scoreSection in scoreSections:
    container.add_widget(scoreSection)

container2 = MyBoxLayout(spacing=10, size=(10000, 210), pos=(100, -100))
container2.add_widget(container)
container2.add_widget(Widget())  # Spacer

root = ScatterPlane(scale=(metrics.mm(210) / 210))  # 210 is what we use in a normal page
root.add_widget(container2)

kivy.base.runTouchApp(root)
