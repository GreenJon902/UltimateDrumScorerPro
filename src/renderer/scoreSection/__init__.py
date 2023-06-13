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

        already_processed_heads = False
        # Check none as if None then will probs get processed in all
        if self._last_note_level_info is not None and note_level_info != self._last_note_level_info:
            already_processed_heads = True
            for i in range(len(self.storage)):
                head_group, head_width = self.head_creator.create(self.ssihs[i].head_group, note_level_info,
                                                                  self.storage[i].note_ids)
                self.ssihs[i].head_width = head_width

        while len(instructions) > 0:  # Organiser adds new commands
            command = instructions.pop(0)[0]
            Logger.debug(f"ScoreSectionRenderer: Processing {command}...")

            if command[0] == "all" or (command[0] == "storage" and command[1] == "set"):
                self.component_organiser.setup(self.canvas)
                for i in range(len(self.storage)):
                    head_group, head_width = self.head_creator.create(None, note_level_info, self.storage[i].note_ids)
                    bar_group, bar_width_min, bar_height = self.bar_creator.create(None, self.storage[i].bars,
                                                                                   self.storage[i].before_flags,
                                                                                   self.storage[i].after_flags,
                                                                                   self.storage[i].slanted_flags)
                    dot_group, dot_width, dot_height = self.dot_creator.create(None, self.storage[i].dots)
                    built_group = self.component_organiser.build(head_group, bar_group, dot_group)
                    ssih = SectionSectionInfoHolder(head_group=head_group, head_width=head_width,
                                             bar_group=bar_group, bar_width_min=bar_width_min, bar_height=bar_height,
                                             dot_group=dot_group, dot_width=dot_width, dot_height=dot_height,
                                             custom_width=self.storage[i].custom_width,
                                             built_group=built_group)
                    self.component_organiser.parent_insert(self.canvas, i, built_group)
                    self.ssihs.insert(i, ssih)

            elif command[0] == "storage" and command[1] == "insert":
                if already_processed_heads:
                    continue

                i = command[2]

                head_group, head_width = self.head_creator.create(None, note_level_info, self.storage[i].note_ids)
                bar_group, bar_width_min, bar_height = self.bar_creator.create(None, self.storage[i].bars,
                                                                               self.storage[i].before_flags,
                                                                               self.storage[i].after_flags,
                                                                               self.storage[i].slanted_flags)
                dot_group, dot_width, dot_height = self.dot_creator.create(None, self.storage[i].dots)
                built_group = self.component_organiser.build(head_group, bar_group, dot_group)
                ssih = SectionSectionInfoHolder(head_group=head_group, head_width=head_width,
                                                bar_group=bar_group, bar_width_min=bar_width_min, bar_height=bar_height,
                                                dot_group=dot_group, dot_width=dot_width, dot_height=dot_height,
                                                custom_width=self.storage[i].custom_width,
                                                built_group=built_group)
                self.component_organiser.parent_insert(self.canvas, i, built_group)
                self.ssihs.insert(i, ssih)

            elif command[0] == "section" and command[1] == "note_ids":
                if already_processed_heads:
                    continue

                section = command[2]
                i = self.storage.index(section)
                head_group, head_width = self.head_creator.create(self.ssihs[i].head_group, note_level_info,
                                                                  self.storage[i].note_ids)
                self.ssihs[i].head_width = head_width

            elif command[0] == "section" and command[1] == "bars":
                section = command[2]
                i = self.storage.index(section)
                bar_group, bar_width_min, bar_height = self.bar_creator.create(None, self.storage[i].bars,
                                                                               self.storage[i].before_flags,
                                                                               self.storage[i].after_flags,
                                                                               self.storage[i].slanted_flags)
                self.ssihs[i].bar_width_min = bar_width_min
                self.ssihs[i].bar_height = bar_height

            elif command[0] == "section" and command[1] == "dots":
                section = command[2]
                i = self.storage.index(section)
                dot_group, dot_width, dot_height = self.dot_creator.create(None, self.storage[i].dots)
                self.ssihs[i].dot_width = dot_width
                self.ssihs[i].dot_height = dot_height

            else:
                Logger.critical(f"ScoreSectionRenderer: Can't process instruction - {command}")

        width, height, section_widths = self.component_organiser.organise(self.ssihs, head_height)
        for i, section_width in enumerate(section_widths):
            self.bar_creator.update_width(self.ssihs[i].bar_group, section_width)
        #self.size = width, height
        Logger.info(f"ScoreSectionRenderer: {time.time() - t}s elapsed!")


    def set_storage(self, storage):
        if self.storage is not None:
            self.storage.unbind_all(self.dispatch_instruction)
        Renderer.set_storage(self, storage)
        self.storage.bind_all(self.dispatch_instruction)
        self.dispatch_instruction("all")



__all__ = ["ScoreSectionRenderer", "SectionSectionInfoHolder"]
