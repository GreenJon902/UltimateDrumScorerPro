from kivy.properties import ObjectProperty

from renderer import Renderer
from renderer.scoreSection.scoreSection_barCreatorBase import ScoreSection_BarCreatorBase
from renderer.scoreSection.scoreSection_componentOrganiserBase import ScoreSection_ComponentOrganiserBase
from renderer.scoreSection.scoreSection_dotCreatorBase import ScoreSection_DotCreatorBase
from renderer.scoreSection.scoreSection_headCreatorBase import ScoreSection_HeadCreatorBase
from scoreStorage.scoreSectionStorage import ScoreSectionStorage


class ScoreSectionRenderer(Renderer):
    storage: ScoreSectionStorage

    component_organiser: ScoreSection_ComponentOrganiserBase = ObjectProperty(allownone=True)

    head_creator: ScoreSection_HeadCreatorBase = ObjectProperty(allownone=True)
    #decoration_creator = ObjectProperty(allownone=True)
    #stem_creator = ObjectProperty(allownone=True)
    bar_creator: ScoreSection_BarCreatorBase = ObjectProperty(allownone=True)
    dot_creator: ScoreSection_DotCreatorBase = ObjectProperty(allownone=True)

    def __init__(self, *args, **kwargs):
        Renderer.__init__(self, *args, **kwargs)
        self.bind(component_organiser=lambda _, __: self.dispatch_instruction("organiser"),
                  head_creator=lambda _, __: self.dispatch_instruction("heads"),
                  bar_creator=lambda _, __: self.dispatch_instruction("bars"),
                  dot_creator=lambda _, __: self.dispatch_instruction("dots"))
        self.dispatch_instruction("all")

    def process_instructions(self, instructions: list[tuple[tuple[any, ...], dict[str, any]]]):
        commands = instructions[:][0][0]

    def set_storage(self, storage):
        if self.storage is not None:
            self.storage.unbind_all(self.process_instructions)
        Renderer.set_storage(self, storage)
        self.storage.bind_all(self.process_instructions)
        self.dispatch_instruction("all")


__all__ = ["ScoreSectionRenderer"]
