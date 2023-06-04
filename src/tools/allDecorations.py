import kivy.base
from kivy import metrics
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.widget import Widget

from renderer.scoreSection import ScoreSectionRenderer
from renderer.scoreSection.scoreSection_normalComponentOrganiser import ScoreSection_NormalComponentOrganiser
from renderer.scoreSection.scoreSection_normalDecorationCreator import ScoreSection_NormalDecorationCreator
from renderer.scoreSection.scoreSection_opacityHeadCreator import ScoreSection_OpacityHeadCreator
from scoreSectionDesigns.decorations import decorations, check_decorations
from scoreStorage.scoreSectionStorage import ScoreSectionStorage, ScoreSectionSectionStorage

check_decorations()

min_decoration_id = 0
max_decoration_id = len(decorations)
decoration_ids = range(min_decoration_id, max_decoration_id)

container_spacing = 5


Builder.load_string("""
<ScoreSectionRenderer>:
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


scoreSections = list()
for decoration in decoration_ids:
    scoreSections.append(ScoreSectionRenderer(ScoreSectionStorage([
        ScoreSectionSectionStorage(decoration_id=decoration),
    ]), decoration_creator=ScoreSection_NormalDecorationCreator((0, 0, 0, 1)),
        component_organiser=ScoreSection_NormalComponentOrganiser(), size_hint=(None, None)))
    scoreSections.append(ScoreSectionRenderer(ScoreSectionStorage([
        ScoreSectionSectionStorage(decoration_id=decoration, note_ids=[1, 2, 3, 4]),
    ]), decoration_creator=ScoreSection_NormalDecorationCreator((0, 0, 0, 1)),
        component_organiser=ScoreSection_NormalComponentOrganiser(),
        head_creator=ScoreSection_OpacityHeadCreator((0, 0, 0, 0), (0, 0, 0, 0)), size_hint=(None, None)))


container = GridLayout(spacing=container_spacing, size_hint_x=1, cols=2)
container.width = sum([decorations[decoration_id]().width + container_spacing for decoration_id in decoration_ids])
for scoreSection in scoreSections:
    container.add_widget(scoreSection)

container2 = MyBoxLayout(spacing=10, size=(10000, 210), pos=(100, -100))
container2.add_widget(container)
container2.add_widget(Widget())  # Spacer

root = ScatterPlane(scale=(metrics.mm(210) / 210))  # 210 is what we use in a normal page
root.add_widget(container2)

kivy.base.runTouchApp(root)
