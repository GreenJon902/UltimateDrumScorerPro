import os

from renderer.scoreSection.scoreSection_normalDecorationCreator import ScoreSection_NormalDecorationCreator
from renderer.scoreSection.scoreSection_normalStemCreator import ScoreSection_NormalStemCreator

os.environ["KCFG_KIVY_LOG_LEVEL"] = "debug"

import kivy.base
from kivy import metrics
from kivy.lang import Builder
from kivy.uix.scatter import ScatterPlane
from kivy.uix.widget import Widget

from renderer.scoreSection import ScoreSectionRenderer
from renderer.scoreSection.scoreSection_normalBarCreator import ScoreSection_NormalBarCreator
from renderer.scoreSection.scoreSection_normalComponentOrganiser import ScoreSection_NormalComponentOrganiser
from renderer.scoreSection.scoreSection_normalDotCreator import ScoreSection_NormalDotCreator
from renderer.scoreSection.scoreSection_opacityHeadCreator import ScoreSection_OpacityHeadCreator
from scoreStorage.scoreSectionStorage import ScoreSectionStorage, ScoreSectionSectionStorage

Builder.load_string("""
<ScatterPlane>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: -2, -2
            size: self.width + 4, self.height + 4
""")


storage = ScoreSectionStorage([
    ScoreSectionSectionStorage(note_ids=[2, 3]),
    ScoreSectionSectionStorage(note_ids=[5, 7, 1], before_flags=2, after_flags=3, bars=1),
    ScoreSectionSectionStorage(note_ids=[5, 6, 1], dots=4, bars=4),
    ScoreSectionSectionStorage(note_ids=[], slanted_flags=2, decoration_id=0)
])

renderer = ScoreSectionRenderer(storage, bar_creator=ScoreSection_NormalBarCreator((0, 0, 0, 1)),
                                dot_creator=ScoreSection_NormalDotCreator((0, 0, 0, 1)),
                                head_creator=ScoreSection_OpacityHeadCreator((0, 0, 0, 1), (0, 0, 0, 0)),
                                component_organiser=ScoreSection_NormalComponentOrganiser(),
                                stem_creator=ScoreSection_NormalStemCreator((0, 0, 0, 1)),
                                decoration_creator=ScoreSection_NormalDecorationCreator((0, 0, 0, 1)))

design_holder = Widget(size_hint=(None, None))
design_holder.add_widget(renderer)
design_holder.size = renderer.size
renderer.bind(size=lambda _, value: setattr(design_holder, "size", value))

root = ScatterPlane(scale=(metrics.mm(1)))
root.pos = 0, 0
root.add_widget(design_holder)

kivy.base.runTouchApp(root)
