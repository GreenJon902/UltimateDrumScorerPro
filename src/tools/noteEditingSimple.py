import os

from kivy import metrics
from kivy.lang import Builder
from kivy.uix.scatter import ScatterPlane

from renderer.scoreSection import ScoreSectionRenderer
from renderer.scoreSection.scoreSection_editorBarCreator import ScoreSection_EditorBarCreator
from renderer.scoreSection.scoreSection_editorDotCreator import ScoreSection_EditorDotCreator
from renderer.scoreSection.scoreSection_normalBarCreator import ScoreSection_NormalBarCreator
from renderer.scoreSection.scoreSection_normalComponentOrganiser import ScoreSection_NormalComponentOrganiser
from renderer.scoreSection.scoreSection_normalDecorationCreator import ScoreSection_NormalDecorationCreator
from renderer.scoreSection.scoreSection_normalDotCreator import ScoreSection_NormalDotCreator
from renderer.scoreSection.scoreSection_normalNoteHeightCalculator import ScoreSection_NormalNoteHeightCalculator
from renderer.scoreSection.scoreSection_normalStemCreator import ScoreSection_NormalStemCreator
from renderer.scoreSection.scoreSection_opacityHeadCreator import ScoreSection_OpacityHeadCreator
from scoreStorage.scoreSectionStorage import ScoreSectionStorage
from selfSizingBoxLayout import SelfSizingBoxLayout
from tests.test_score_section import update

os.environ["KCFG_INPUT_MOUSE"] = "mouse,multitouch_on_demand"

import kivy.base
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

Builder.load_string("""
<ScoreSectionRenderer>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: -2, -2
            size: self.width + 4, self.height + 4
            
<BoxLayout>:
    canvas.before:
        Color:
            rgba: 0.7, 0.7, 0.7, 1
        Rectangle:
            pos: -1000, -1000
            size: self.width + 2000, self.height + 2000
""")

start_location = 0

scoreSectionStorage = ScoreSectionStorage()
for n in range(start_location + 1):
    update(scoreSectionStorage)

renderers = []

if True:  # Normal
    renderers.append(ScoreSectionRenderer(scoreSectionStorage, bar_creator=ScoreSection_NormalBarCreator((0, 0, 0, 1)),
                                          dot_creator=ScoreSection_NormalDotCreator((0, 0, 0, 1)),
                                          head_creator=ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0)),
                                          component_organiser=ScoreSection_NormalComponentOrganiser(),
                                          stem_creator=ScoreSection_NormalStemCreator((0, 0, 0, 1)),
                                          decoration_creator=ScoreSection_NormalDecorationCreator((0, 0, 0, 1)),
                                          note_height_calculator=ScoreSection_NormalNoteHeightCalculator()))

if True:  # Fast Editor
    renderers.append(ScoreSectionRenderer(scoreSectionStorage, bar_creator=ScoreSection_EditorBarCreator((0, 0, 0, 1), (0, 0, 0, 0.2)),
                                          dot_creator=ScoreSection_EditorDotCreator((0, 0, 0, 1), (0, 0, 0, 0.2)),
                                          head_creator=ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0.2)),
                                          component_organiser=ScoreSection_NormalComponentOrganiser(),
                                          decoration_creator=ScoreSection_NormalDecorationCreator((0, 0, 0, 1)),
                                          note_height_calculator=ScoreSection_NormalNoteHeightCalculator()))

root = ScatterPlane(scale=(metrics.mm(210) / 210))  # 210 is what we use in a normal page
container = SelfSizingBoxLayout(orientation="vertical", anchor="middle", spacing=5)
for renderer in renderers:
    container.add_widget(renderer)
root.add_widget(container)
container.do_layout()

boxLayout = BoxLayout(orientation="vertical")
boxLayout.add_widget(root)
boxLayout.add_widget(Button(text="next", on_release=lambda _: update(scoreSectionStorage), size_hint_y=0.2))

kivy.base.runTouchApp(boxLayout)
