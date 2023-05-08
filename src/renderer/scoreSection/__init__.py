from kivy.properties import ObjectProperty

from renderer import Renderer
from scoreStorage.scoreSectionStorage import ScoreSectionStorage


class TextRenderer(Renderer):
    storage: ScoreSectionStorage

    component_organiser = ObjectProperty()
    head_creator = ObjectProperty()
    stem_creator = ObjectProperty()
    bar_creator = ObjectProperty()
