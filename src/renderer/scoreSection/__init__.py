import time

from kivy import Logger
from kivy.graphics import InstructionGroup
from kivy.properties import ObjectProperty

from renderer import Renderer
from renderer.scoreSection.scoreSection_barCreatorBase import ScoreSection_BarCreatorBase
from renderer.scoreSection.scoreSection_componentOrganiserBase import ScoreSection_ComponentOrganiserBase
from renderer.scoreSection.scoreSection_decorationCreatorBase import ScoreSection_DecorationCreatorBase
from renderer.scoreSection.scoreSection_dotCreatorBase import ScoreSection_DotCreatorBase
from renderer.scoreSection.scoreSection_headCreatorBase import ScoreSection_HeadCreatorBase
from renderer.scoreSection.scoreSection_noteHeightCalculatorBase import ScoreSection_NoteHeightCalculatorBase
from renderer.scoreSection.scoreSection_stemCreatorBase import ScoreSection_StemCreatorBase
from scoreStorage.scoreSectionStorage import ScoreSectionStorage


class ScoreSectionRenderer(Renderer):
    storage: ScoreSectionStorage

    component_organiser: ScoreSection_ComponentOrganiserBase = ObjectProperty(allownone=True)

    note_height_calculator: ScoreSection_NoteHeightCalculatorBase = ObjectProperty(allownone=True)
    head_creator: ScoreSection_HeadCreatorBase = ObjectProperty(allownone=True)
    decoration_creator: ScoreSection_DecorationCreatorBase = ObjectProperty(allownone=True)
    stem_creator: ScoreSection_StemCreatorBase = ObjectProperty(allownone=True)
    bar_creator: ScoreSection_BarCreatorBase = ObjectProperty(allownone=True)
    dot_creator: ScoreSection_DotCreatorBase = ObjectProperty(allownone=True)

    lowest_note_info: list[tuple[float, int]]
    head_groups: list[InstructionGroup]

    existent_nids = list[int]

    def __init__(self, *args, **kwargs):
        self.existent_nids = []
        self.lowest_note_info = []
        self.head_groups = []
        Renderer.__init__(self, *args, **kwargs)
        self.bind(component_organiser=lambda _, __: self.dispatch_instruction("organiser"),
                  head_creator=lambda _, __: self.dispatch_instruction("heads"),
                  bar_creator=lambda _, __: self.dispatch_instruction("bars"),
                  dot_creator=lambda _, __: self.dispatch_instruction("dots"))
        self.dispatch_instruction("all")

    def process_instructions(self, instructions: list[tuple[tuple[any, ...], dict[str, any]]]):
        Logger.info(f"ScoreSectionRenderer: Updating {self} with {instructions}...")
        t = time.time()

        while len(instructions) > 0:  # Organiser adds new commands
            command = instructions.pop(0)[0]
            Logger.debug(f"ScoreSectionRenderer: Processing {command}...")

            if command[0] == "all":
                if self.component_organiser is not None:
                    self.component_organiser.setup(self.canvas)
                else:
                    Logger.warning("ScoreSectionRenderer: No organiser supplied")  # Warn as no organiser means no
                                                                                   # rendering, which makes no sense
                new_commands = list()
                for i in range(len(self.storage)):
                    head_info = self.do_head(i)
                    self.lowest_note_info.insert(i, head_info[3] if head_info is not None else None)
                    self.head_groups.insert(i, head_info[0] if head_info is not None else None)
                    bar_info = self.do_bar(i)
                    dot_info = self.do_dot(i)
                    stem_info = self.do_stem()
                    decoration_info = self.do_decoration(i)

                    if self.component_organiser is not None:
                        new_commands += self.component_organiser.add_section(i, head_info=head_info, bar_info=bar_info,
                                                                             dot_info=dot_info, stem_info=stem_info,
                                                                             decoration_info=decoration_info)
                    else:
                        Logger.warning("ScoreSectionRenderer: No organiser supplied")  # Warn as no organiser means no
                                                                                       # rendering, which makes no sense
                    self.update_stem_height(stem_info[0], i)
                Logger.debug(f"ScoreSectionRenderer: Got new instructions: {new_commands}")
                instructions += new_commands  # TODO: Remove duplicates

            elif command[0] == "update_bar_width":
                self.update_bar_width(command[1], command[2])

            elif command[0] == "set_size":
                self.width = command[1]
                self.height = command[2]

            elif command[0] == "update_decoration_height":
                self.update_decoration_height(command[1], command[2], command[3], command[4])

            elif command[0] == "update_heads":
                self.update_heads()

            elif command[0] == "storage":
                if command[1] == "insert":
                    i = command[2]

                    head_info = self.do_head(i)
                    self.lowest_note_info.insert(i, head_info[3] if head_info is not None else None)
                    self.head_groups.insert(i, head_info[0] if head_info is not None else None)
                    bar_info = self.do_bar(i)
                    dot_info = self.do_dot(i)
                    stem_info = self.do_stem()
                    decoration_info = self.do_decoration(i)

                    if self.component_organiser is not None:
                        new_commands = self.component_organiser.add_section(i, head_info=head_info, bar_info=bar_info,
                                                                            dot_info=dot_info, stem_info=stem_info,
                                                                            decoration_info=decoration_info)
                        Logger.debug(f"ScoreSectionRenderer: Got new instructions: {new_commands}")
                        instructions += new_commands  # TODO: Remove duplicates
                    else:
                        Logger.warning("ScoreSectionRenderer: No organiser supplied")  # Warn as no organiser means no
                                                                                       # rendering, which makes no sense

                    self.update_stem_height(stem_info[0], i)


            else:
                Logger.critical(f"ScoreSectionRenderer: Can't process instruction - {command}")

        Logger.info(f"ScoreSectionRenderer: {time.time() - t}s elapsed!")

    def check_existent_nids(self):
        nids = set()
        for section in self.storage:
            nids.update(section.note_ids)

        difference = nids.symmetric_difference(self.existent_nids)
        if len(difference) != 0:
            self.existent_nids = nids

            self.dispatch_instruction("update_heads")

    def do_head(self, index):
        if self.head_creator is None:
            return None
        self.check_existent_nids()
        if self.note_height_calculator is None:
            return None
        note_levels = self.note_height_calculator.get(self.existent_nids)
        return self.head_creator.create(self.storage[index].note_ids, note_levels)

    def do_bar(self, index):
        if self.bar_creator is None:
            return None
        return self.bar_creator.create(self.storage[index].bars, self.storage[index].before_flags,
                                       self.storage[index].after_flags, self.storage[index].slanted_flags)

    def do_dot(self, index):
        if self.dot_creator is None:
            return None
        return self.dot_creator.create(self.storage[index].dots)

    def do_stem(self):
        if self.stem_creator is None:
            return None
        return self.stem_creator.create()

    def do_decoration(self, index):
        if self.decoration_creator is None:
            return None
        return self.decoration_creator.create(self.storage[index].decoration_id)

    def update_stem_height(self, stem_group, index):
        if self.stem_creator is None:
            return
            self.check_existent_nids()
        if self.note_height_calculator is None:
            return None
        note_heights = self.note_height_calculator.get(self.existent_nids)
        self.stem_creator.update_height(stem_group, note_heights, self.storage[index].note_ids)

    def update_bar_width(self, bar_group, width):
        if self.bar_creator is None:
            return
        self.bar_creator.update_width(bar_group, width)

    def set_storage(self, storage):
        if self.storage is not None:
            self.storage.unbind_all(self.dispatch_instruction)
        Renderer.set_storage(self, storage)
        self.storage.bind_all(self.dispatch_instruction)
        self.dispatch_instruction("all")

    def update_decoration_height(self, decoration_group, head_height, overall_height, index):
        if self.decoration_creator is None:
            return
        self.decoration_creator.update_height(decoration_group, head_height, overall_height, self.storage[index].decoration_id)

    def update_heads(self):
        if self.head_creator is None:
            return
        self.check_existent_nids()
        if self.note_height_calculator is None:
            return None
        note_heights = self.note_height_calculator.get(self.existent_nids)
        for i in range(len(self.storage)):
            head_info = self.head_creator.update(self.storage[i].note_ids, note_heights, self.head_groups[i])
            lowest_note_info = head_info[3] if head_info is not None else None
            if lowest_note_info != self.lowest_note_info[i]:
                self.lowest_note_info[i] = lowest_note_info
                self.update_stem_height()


__all__ = ["ScoreSectionRenderer"]
