from kivy.properties import ObjectProperty

from renderer import Renderer
from scoreStorage.scoreSectionStorage import ScoreSectionStorage


class ScoreSectionRenderer(Renderer):
    storage: ScoreSectionStorage

    component_organiser = ObjectProperty(allownone=True)

    head_creator = ObjectProperty(allownone=True)
    decoration_creator = ObjectProperty(allownone=True)
    stem_creator = ObjectProperty(allownone=True)
    bar_creator = ObjectProperty(allownone=True)
    dot_creator = ObjectProperty(allownone=True)


__all__ = ["ScoreSectionRenderer"]
