import time

from kivy import Logger
from kivy.properties import ObjectProperty

from renderer import Renderer
from renderer.scoreSection.scoreSection_barCreatorBase import ScoreSection_BarCreatorBase
from renderer.scoreSection.scoreSection_componentOrganiserBase import ScoreSection_ComponentOrganiserBase
from renderer.scoreSection.scoreSection_dotCreatorBase import ScoreSection_DotCreatorBase
from renderer.scoreSection.scoreSection_headCreatorBase import ScoreSection_HeadCreatorBase
from renderer.scoreSection.scoreSection_stemCreatorBase import ScoreSection_StemCreatorBase
from scoreStorage.scoreSectionStorage import ScoreSectionStorage


class ScoreSectionRenderer(Renderer):
    storage: ScoreSectionStorage

    component_organiser: ScoreSection_ComponentOrganiserBase = ObjectProperty(allownone=True)

    head_creator: ScoreSection_HeadCreatorBase = ObjectProperty(allownone=True)
    #decoration_creator = ObjectProperty(allownone=True)
    stem_creator: ScoreSection_StemCreatorBase = ObjectProperty(allownone=True)
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
        Logger.info(f"ScoreSectionRenderer: Updating {self} with {instructions}...")
        t = time.time()

        for command in instructions:
            command = command[0]
            Logger.debug(f"ScoreSectionRenderer: Processing {command}...")

            if command[0] == "all":
                if self.component_organiser is not None:
                    self.component_organiser.setup(self.canvas)
                else:
                    Logger.warning("ScoreSectionRenderer: No organiser supplied")  # Warn as no organiser means no
                                                                                   # rendering, which makes no sense

                for i in range(len(self.storage)):
                    head_info = self.do_head(i)
                    bar_info = self.do_bar(i)
                    dot_info = self.do_dot(i)
                    stem_info = self.do_stem(i)

                    self.update_stem_height(head_info, stem_info)

                    if self.component_organiser is not None:
                        self.component_organiser.add_section(i, head_info=head_info, bar_info=bar_info,
                                                             dot_info=dot_info, stem_info=stem_info)
                    else:
                        Logger.warning("ScoreSectionRenderer: No organiser supplied")  # Warn as no organiser means no
                                                                                       # rendering, which makes no sense
            else:
                Logger.critical(f"ScoreSectionRenderer: Can't process instruction - {command}")

        Logger.info(f"ScoreSectionRenderer: {time.time() - t}s elapsed!")

    def do_head(self, index):
        if self.head_creator is None:
            return None
        nids = set()
        for section in self.storage:
            nids.update(section.note_ids)
        return self.head_creator.create(self.storage[index].note_ids, nids)

    def do_bar(self, index):
        if self.bar_creator is None:
            return None
        return self.bar_creator.create(self.storage[index].bars, self.storage[index].before_flags,
                                       self.storage[index].after_flags)

    def do_dot(self, index):
        if self.dot_creator is None:
            return None
        return self.dot_creator.create(self.storage[index].dots)

    def do_stem(self, index):
        if self.stem_creator is None:
            return None
        return self.stem_creator.create()

    def update_stem_height(self, head_info, stem_info):
        if head_info is None or stem_info is None or self.stem_creator is None:
            return
        self.stem_creator.update_height(stem_info, head_info[3])

    def set_storage(self, storage):
        if self.storage is not None:
            self.storage.unbind_all(self.process_instructions)
        Renderer.set_storage(self, storage)
        self.storage.bind_all(self.process_instructions)
        self.dispatch_instruction("all")


__all__ = ["ScoreSectionRenderer"]
