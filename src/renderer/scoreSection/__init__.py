from __future__ import annotations

import time
import typing

from kivy import Logger
from kivy.graphics import InstructionGroup
from kivy.properties import ObjectProperty

from renderer import Renderer

if typing.TYPE_CHECKING:
    from renderer.scoreSection.scoreSection_barCreatorBase import ScoreSection_BarCreatorBase
    from renderer.scoreSection.scoreSection_componentOrganiserBase import ScoreSection_ComponentOrganiserBase
    from renderer.scoreSection.scoreSection_decorationCreatorBase import ScoreSection_DecorationCreatorBase
    from renderer.scoreSection.scoreSection_dotCreatorBase import ScoreSection_DotCreatorBase
    from renderer.scoreSection.scoreSection_headCreatorBase import ScoreSection_HeadCreatorBase
    from renderer.scoreSection.scoreSection_noteHeightCalculatorBase import ScoreSection_NoteHeightCalculatorBase
    from renderer.scoreSection.scoreSection_stemCreatorBase import ScoreSection_StemCreatorBase
from scoreStorage.scoreSectionStorage import ScoreSectionStorage


class SectionSectionInfoHolder:
    head_group: InstructionGroup
    dot_group: InstructionGroup
    bar_group: InstructionGroup
    built_group: InstructionGroup
    head_width: float
    stem_connection_point: float
    stem_group: float
    dot_width: float
    dot_height: float
    bar_width_min: float
    bar_height: float
    custom_width: float

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ScoreSectionRenderer(Renderer):
    storage: ScoreSectionStorage

    component_organiser: ScoreSection_ComponentOrganiserBase = ObjectProperty(allownone=True)

    note_height_calculator: ScoreSection_NoteHeightCalculatorBase = ObjectProperty(allownone=True)
    head_creator: ScoreSection_HeadCreatorBase = ObjectProperty(allownone=True)
    decoration_creator: ScoreSection_DecorationCreatorBase = ObjectProperty(allownone=True)
    stem_creator: ScoreSection_StemCreatorBase = ObjectProperty(allownone=True)
    bar_creator: ScoreSection_BarCreatorBase = ObjectProperty(allownone=True)
    dot_creator: ScoreSection_DotCreatorBase = ObjectProperty(allownone=True)

    ssihs: list[SectionSectionInfoHolder]
    _last_note_level_info = None

    def __init__(self, *args, **kwargs):
        self.ssihs = []
        Renderer.__init__(self, *args, **kwargs)
        self.bind(component_organiser=lambda _, __: self.dispatch_instruction("organiser"),
                  head_creator=lambda _, __: self.dispatch_instruction("heads"),
                  bar_creator=lambda _, __: self.dispatch_instruction("bars"),
                  dot_creator=lambda _, __: self.dispatch_instruction("dots"))
        self.dispatch_instruction("all")

    def process_instructions(self, instructions: list[tuple[tuple[any, ...], dict[str, any]]]):
        Logger.info(f"ScoreSectionRenderer: Updating {self} with {instructions}...")
        t = time.time()

        existant_nids = set()
        for section in self.storage:
            existant_nids.update(section.note_ids)
        note_level_info, head_height = self.note_height_calculator.get(existant_nids)

        while len(instructions) > 0:  # Organiser adds new commands
            command = instructions.pop(0)[0]
            Logger.debug(f"ScoreSectionRenderer: Processing {command}...")

            if command[0] == "all" or (command[0] == "storage" and command[1] == "set"):
                self.component_organiser.setup(self.canvas)
                self.ssihs.clear()
                for i in range(len(self.storage)):
                    self.make_section_section(i, note_level_info)

            elif command[0] == "storage" and command[1] == "insert":
                self.make_section_section(command[2], note_level_info)

            elif command[0] == "storage" and command[1] == "remove":
                self.component_organiser.parent_remove(self.canvas, command[2])
                self.ssihs.pop(command[2])

            elif command[0] == "section" and command[1] == "note_ids":
                section = command[2]
                i = self.storage.index(section)
                head_group, head_width, stem_connection_point = self.head_creator.create(self.ssihs[i].head_group, note_level_info,
                                                                  self.storage[i].note_ids)
                self.ssihs[i].head_width = head_width
                self.ssihs[i].stem_connection_point = stem_connection_point

            elif command[0] == "section" and (command[1] == "bars" or
                                              command[1] == "before_flags" or
                                              command[1] == "after_flags" or
                                              command[1] == "slanted_flags"):
                i = self.storage.index(command[2])
                bar_group, bar_width_min, bar_height = self.bar_creator.create(self.ssihs[i].bar_group,
                                                                               self.storage[i].bars,
                                                                               self.storage[i].before_flags,
                                                                               self.storage[i].after_flags,
                                                                               self.storage[i].slanted_flags)
                self.ssihs[i].bar_width_min = bar_width_min
                self.ssihs[i].bar_height = bar_height

            elif command[0] == "section" and command[1] == "dots":
                i = self.storage.index(command[2])
                dot_group, dot_width, dot_height = self.dot_creator.create(None, self.storage[i].dots)
                self.ssihs[i].dot_width = dot_width
                self.ssihs[i].dot_height = dot_height

            else:
                Logger.critical(f"ScoreSectionRenderer: Can't process instruction - {command}")


        if note_level_info != self._last_note_level_info:  # Do after so indexes of all ssihs are correct
            for i in range(len(self.storage)):
                head_group, head_width, stem_connection_point = self.head_creator.create(self.ssihs[i].head_group,
                                                                                         note_level_info,
                                                                                         self.storage[i].note_ids)
                self.ssihs[i].head_width = head_width
                self.ssihs[i].stem_connection_point = stem_connection_point

        width, height, section_widths = self.component_organiser.organise(self.ssihs, head_height)
        for i, section_width in enumerate(section_widths):
            self.bar_creator.update_width(self.ssihs[i].bar_group, section_width)
        for ssih in self.ssihs:
            self.stem_creator.update_height(ssih.stem_group, ssih.stem_connection_point, height, head_height)
        self.size = width, height
        Logger.info(f"ScoreSectionRenderer: {time.time() - t}s elapsed!")


    def make_section_section(self, i, note_level_info):
        head_group, head_width, stem_connection_point = self.head_creator.create(None, note_level_info,
                                                                                 self.storage[i].note_ids)
        bar_group, bar_width_min, bar_height = self.bar_creator.create(None, self.storage[i].bars,
                                                                       self.storage[i].before_flags,
                                                                       self.storage[i].after_flags,
                                                                       self.storage[i].slanted_flags)
        dot_group, dot_width, dot_height = self.dot_creator.create(None, self.storage[i].dots)
        stem_group = self.stem_creator.create()
        built_group = self.component_organiser.build(head_group, bar_group, dot_group, stem_group)
        ssih = SectionSectionInfoHolder(head_group=head_group, head_width=head_width,
                                        stem_connection_point=stem_connection_point,
                                        bar_group=bar_group, bar_width_min=bar_width_min, bar_height=bar_height,
                                        dot_group=dot_group, dot_width=dot_width, dot_height=dot_height,
                                        custom_width=self.storage[i].custom_width,
                                        stem_group=stem_group,
                                        built_group=built_group)
        self.component_organiser.parent_insert(self.canvas, i, built_group)
        self.ssihs.insert(i, ssih)

    def set_storage(self, storage):
        if self.storage is not None:
            self.storage.unbind_all(self.dispatch_instruction)
        Renderer.set_storage(self, storage)
        self.storage.bind_all(self.dispatch_instruction)
        self.dispatch_instruction("all")



__all__ = ["ScoreSectionRenderer", "SectionSectionInfoHolder"]
