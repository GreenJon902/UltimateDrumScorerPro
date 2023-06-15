from __future__ import annotations

import time
import typing
from typing import Optional

from kivy import Logger
from kivy.graphics import InstructionGroup
from kivy.properties import ObjectProperty

from renderer import Renderer
from scoreSectionDesigns.notes import notes

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
    stem_group: InstructionGroup
    decoration_group: InstructionGroup
    head_width: float
    lowest_note_id: Optional[int]
    dot_width: float
    dot_height: float
    bar_width_min: float
    bar_height: float
    custom_width: float
    decoration_width: float
    decoration_height_min: float

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ScoreSectionRenderer(Renderer):
    """
    ScoreSectionRenderer renders a section of notes and other parts that are of actual musical value.
    """

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

        if self.note_height_calculator is None:
            raise Exception("Cannot render score section without note_height_calculator")
        if self.component_organiser is None:
            raise Exception("Cannot render score section without component_organiser")

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
                self.update_heads(self.storage.index(command[2]), note_level_info)

            elif command[0] == "section" and (command[1] == "bars" or
                                              command[1] == "before_flags" or
                                              command[1] == "after_flags" or
                                              command[1] == "slanted_flags"):
                self.update_bars(self.storage.index(command[2]))

            elif command[0] == "section" and command[1] == "dots":
                self.update_dots(self.storage.index(command[2]))

            elif command[0] == "section" and command[1] == "decoration_id":
                self.update_decoration(self.storage.index(command[2]))

            else:
                Logger.critical(f"ScoreSectionRenderer: Can't process instruction - {command}")


        self.check_heads(note_level_info)  # Do after so indexes of all ssihs are correct

        width, height, bar_widths = self.component_organiser.organise(self.ssihs, head_height)
        Logger.debug(f"ScoreSectionRenderer: Organised, size is now {width, height}")
        self.update_bar_widths(bar_widths)
        self.update_stem_heights(note_level_info, height, head_height)
        self.update_decoration_heights(height, head_height)
        self.size = width, height
        Logger.info(f"ScoreSectionRenderer: {time.time() - t}s elapsed!")


    def make_section_section(self, i, note_level_info):
        head_group, head_width, lowest_note_id = self.do_heads(i, note_level_info)
        bar_group, bar_width_min, bar_height = self.do_bars(i)
        dot_group, dot_width, dot_height = self.do_dots(i)
        stem_group = self.do_stem()
        decoration_group, decoration_width, decoration_height_min = self.do_decoration(i)
        built_group = self.component_organiser.build(head_group, bar_group, dot_group, stem_group, decoration_group)
        ssih = SectionSectionInfoHolder(head_group=head_group, head_width=head_width,
                                        lowest_note_id=lowest_note_id,
                                        bar_group=bar_group, bar_width_min=bar_width_min, bar_height=bar_height,
                                        dot_group=dot_group, dot_width=dot_width, dot_height=dot_height,
                                        custom_width=self.storage[i].custom_width,
                                        stem_group=stem_group,
                                        built_group=built_group,
                                        decoration_group=decoration_group, decoration_width=decoration_width,
                                        decoration_height_min=decoration_height_min)
        self.component_organiser.parent_insert(self.canvas, i, built_group)
        self.ssihs.insert(i, ssih)

    def set_storage(self, storage):
        if self.storage is not None:
            self.storage.unbind_all(self.dispatch_instruction)
        Renderer.set_storage(self, storage)
        self.storage.bind_all(self.dispatch_instruction)
        self.dispatch_instruction("all")

    def do_heads(self, i, note_level_info, group=None):
        if self.head_creator is None:
            return None, 0, None
        head_group, head_width, lowest_note_id = self.head_creator.create(group, note_level_info,
                                                                          self.storage[i].note_ids)
        return head_group, head_width, lowest_note_id

    def update_heads(self, i, note_level_info):
        if self.head_creator is None:
            return
        head_group, head_width, lowest_note_id = self.do_heads(i, note_level_info, self.ssihs[i].head_group)
        self.ssihs[i].head_width = head_width
        self.ssihs[i].lowest_note_id = lowest_note_id

    def check_heads(self, note_level_info):
        """
        Checks whether head heights have changed and all heads need to be redrawn.
        """
        if self.head_creator is None:
            return
        if note_level_info != self._last_note_level_info:
            for i in range(len(self.storage)):
                head_group, head_width, lowest_note_id = self.head_creator.create(self.ssihs[i].head_group,
                                                                                  note_level_info,
                                                                                  self.storage[i].note_ids)
                self.ssihs[i].head_width = head_width
                self.ssihs[i].lowest_note_id = lowest_note_id

            self._last_note_level_info = note_level_info

    def do_bars(self, i, group=None):
        if self.bar_creator is None:
            return None, 0, 0
        bar_group, bar_width_min, bar_height = self.bar_creator.create(group,
                                                                       self.storage[i].bars,
                                                                       self.storage[i].before_flags,
                                                                       self.storage[i].after_flags,
                                                                       self.storage[i].slanted_flags)
        return bar_group, bar_width_min, bar_height

    def update_bars(self, i):
        if self.bar_creator is None:
            return
        bar_group, bar_width_min, bar_height = self.do_bars(i, self.ssihs[i].bar_group)
        self.ssihs[i].bar_width_min = bar_width_min
        self.ssihs[i].bar_height = bar_height

    def update_bar_widths(self, bar_widths):
        if self.bar_creator is None:
            return
        for i, bar_width in enumerate(bar_widths):
            self.bar_creator.update_width(self.ssihs[i].bar_group, bar_width)

    def do_dots(self, i, group=None):
        if self.dot_creator is None:
            return None, 0, 0
        dot_group, dot_width, dot_height = self.dot_creator.create(group, self.storage[i].dots)
        return dot_group, dot_width, dot_height

    def update_dots(self, i):
        if self.dot_creator is None:
            return
        dot_group, dot_width, dot_height = self.do_dots(i, self.ssihs[i].dot_group)
        self.ssihs[i].dot_width = dot_width
        self.ssihs[i].dot_height = dot_height

    def do_stem(self):
        if self.stem_creator is None:
            return None
        stem_group = self.stem_creator.create()
        return stem_group

    def update_stem_heights(self, note_level_info, height, head_height):
        if self.stem_creator is None:
            return
        for ssih in self.ssihs:
            note_height = None
            stem_connection_offset = None
            if ssih.lowest_note_id is not None:
                lowest_note_level = notes[ssih.lowest_note_id].note_level
                for note_level, note_height in note_level_info:
                    if note_level == lowest_note_level:
                        break
                stem_connection_offset = notes[ssih.lowest_note_id].stem_connection_offset
            self.stem_creator.update_height(ssih.stem_group, note_height, stem_connection_offset, height, head_height)

    def do_decoration(self, i, group=None):
        if self.decoration_creator is None:
            return None, 0, 0
        decoration_group, decoration_width, decoration_height_min = \
            self.decoration_creator.create(group, self.storage[i].decoration_id)
        return decoration_group, decoration_width, decoration_height_min

    def update_decoration(self, i):
        if self.decoration_creator is None:
            return None

        decoration_group, decoration_width, decoration_height_min = self.do_decoration(i,
                                                                                       self.ssihs[i].decoration_group)
        self.ssihs[i].decoration_width = decoration_width
        self.ssihs[i].decoration_height_min = decoration_height_min

    def update_decoration_heights(self, height, head_height):
        if self.decoration_creator is None:
            return
        for i, ssih in enumerate(self.ssihs):
            self.decoration_creator.update_height(ssih.decoration_group, height, head_height,
                                                  self.storage[i].decoration_id)


__all__ = ["ScoreSectionRenderer", "SectionSectionInfoHolder"]
