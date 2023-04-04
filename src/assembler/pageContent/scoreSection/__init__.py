import time
from typing import Optional

from kivy import Logger
from kivy.clock import Clock
from kivy.graphics import Line, Canvas, PushMatrix, PopMatrix, Translate, InstructionGroup, Color
from kivy.properties import ObjectProperty, ListProperty

from argumentTrigger import ArgumentTrigger
from assembler.pageContent import PageContent
from assembler.pageContent.scoreSection.noteHeightCalculator import NoteHeightCalculator
from score import ScoreSectionStorage, ScoreSectionSectionStorage
from score.notes import *


def set_width(obj, width):
    obj.width = width


def set_points(obj: Line, points):
    obj.points = points


class ScoreSection(PageContent):
    score: ScoreSectionStorage = ObjectProperty(defaultvalue=ScoreSectionStorage())
    _old_score: Optional[ScoreSectionStorage] = None
    stem_top: float = NumericProperty()
    section_widths: list[float] = ListProperty()

    head_canvas: Canvas  # Contains stems
    head_canvas_container: Canvas
    head_canvas_translate: Translate

    bar_canvas: Canvas  # Contains stems
    bar_canvas_container: Canvas
    bar_canvas_translate: Translate

    update = None
    update_size = None

    noteHeightCalculator: NoteHeightCalculator

    def __init__(self, *args, **kwargs):
        self.update = ArgumentTrigger(self._update, -1, True)
        self.update_size = Clock.create_trigger(self._update_size, -1)
        self.noteHeightCalculator = NoteHeightCalculator()

        self.head_canvas_container = Canvas()
        self.head_canvas = Canvas()
        self.head_canvas_translate = Translate()
        self.head_canvas_container.add(PushMatrix())
        self.head_canvas_container.add(self.head_canvas_translate)
        self.head_canvas_container.add(self.head_canvas)
        self.head_canvas_container.add(PopMatrix())

        self.bar_canvas_container = Canvas()
        self.bar_canvas = Canvas()
        self.bar_canvas_translate = Translate(0, 0, 0)
        self.bar_canvas_container.add(PushMatrix())
        self.bar_canvas_container.add(self.bar_canvas_translate)
        self.bar_canvas_container.add(self.bar_canvas)
        self.bar_canvas_container.add(PopMatrix())

        PageContent.__init__(self, *args, **kwargs)

        self.fbind("section_widths", self.update_size)
        for note in self.noteHeightCalculator.note_objects.values():
            note.fbind("y", self.update_size)
        self.update_size()

        self.canvas.add(self.head_canvas_container)
        self.canvas.add(self.bar_canvas_container)
        self.on_score(self, self.score)

    def _update_size(self, _):
        self.width = sum(self.section_widths)
        lowest_note_y = min(note.y for note in self.noteHeightCalculator.note_objects.values())
        max_bar_height = (max(((section.bars + max(section.before_flags, section.after_flags, section.slanted_flags))
                               for section in self.score), default=0) - 1) * bar_height
        if max_bar_height < 0:
            max_bar_height = 0
        self.height = -lowest_note_y + max_bar_height

        self.head_canvas_translate.y = -lowest_note_y
        self.head_canvas_translate.flag_update()
        self.stem_top = self.height + lowest_note_y  # Cause its being translated by lowest y

        self.bar_canvas_translate.y = -lowest_note_y + max_bar_height
        self.bar_canvas_translate.flag_update()

    def on_score(self, _, value):
        if self._old_score is not None:
            self._old_score.unbind_all(self.update)

        self._old_score = value
        value.bind_all(self.update)
        self.noteHeightCalculator.score = value

        self.update("all")

    def _update(self, changes: list[tuple[tuple[any], dict[str, any]]]):
        Logger.info(f"ScoreSection: Updating {self} with {changes}...")
        t = time.time()

        # TODO: optimize by skipping stuff that gets overwritten (e.g. add bar before full redraw)
        for change in changes:
            change = change[0]  # We don't care about kwargs
            Logger.debug(f"ScoreSection: Changing {change}")

            if change[0] == "all" or (change[0] == "storage" and change[1] == "set"):
                self.full_redraw()
            elif change[0] == "storage" and change[1] == "insert":
                self.add_section(change[2])
                pass
            elif change[0] == "section" and change[1] == "note_ids":
                self.update_section_notes(self.score.index(change[2]))
                pass
            elif change[0] == "section" and (change[1] == "bars" or change[1] == "before_flags" or change[1] ==
                                             "after_flags" or change[1] == "slanted_flags"):
                self.update_section_bars(self.score.index(change[2]))
                pass
            else:
                raise NotImplementedError(f"Score section doesn't know how to change {change}")

        Logger.info(f"ScoreSection: {time.time() - t}s elapsed!")


    def full_redraw(self):
        self.head_canvas.clear()
        self.bar_canvas.clear()
        for i in range(len(self.score)):
            self.add_section(i)

    def add_section(self, index):
        head_group, width = self._make_head_group_from_section(self.score[index])
        self.head_canvas.insert(index, head_group)
        self.section_widths.insert(index, width)

        group = self._make_bar_group_from_section(self.score[index])
        self.bar_canvas.insert(index, group)
        self.update_bar_width(index)

    def update_section_notes(self, index):
        group, width = self._make_head_group_from_section(self.score[index])
        self.head_canvas.children[index].children = group.children  # For some reason we can't change the child, only
                                                                    # the child's children
        self.head_canvas.flag_update()
        self.section_widths[index] = width

        self.update_bar_width(index)

    def update_section_bars(self, index):
        group = self._make_bar_group_from_section(self.score[index])
        self.bar_canvas.children[index].children = group.children  # For some reason we can't change the child, only
                                                                   # the child's children
        self.bar_canvas.flag_update()
        self.update_bar_width(index)

        self.update_size()


    # noinspection PyMethodMayBeStatic
    def _make_bar_group_from_section(self, section: ScoreSectionSectionStorage):
        group = InstructionGroup()
        group.add(Color(rgba=(0, 0, 0, 1)))

        bar_group = InstructionGroup()
        before_flags_group = InstructionGroup()
        after_flags_group = InstructionGroup()
        special_flags_group = InstructionGroup()

        n = 0
        for n in range(section.bars):
            bar_group.add(Line(points=(0, -n * bar_height, 0, -n * bar_height), width=bar_width))  # Minus as draw from
                                                                                                   # top
        n += section.bars >= 1   # If loops once then n is 0 so add 1
        for n2 in range(section.before_flags):
            n3 = n + n2
            before_flags_group.add(Line(points=(0, -n3 * bar_height, flag_length, -n3 * bar_height), width=bar_width))
        for n2 in range(section.after_flags):
            n3 = n + n2
            after_flags_group.add(Line(points=(0, -n3 * bar_height, 0, -n3 * bar_height), width=bar_width))
        for n2 in range(section.slanted_flags):
            n3 = n + n2
            special_flags_group.add(Line(points=(0, -n3 * bar_height, 0, -n3 * bar_height - slanted_flag_height_offset),
                                         width=bar_width))

        group.add(bar_group)
        group.add(before_flags_group)
        group.add(after_flags_group)
        group.add(special_flags_group)

        group.add(Translate())
        return group

    def _make_head_group_from_section(self, section: ScoreSectionSectionStorage):
        self.noteHeightCalculator.update()

        group = InstructionGroup()

        width = 0
        if len(section.note_ids) != 0:
            # Heads ------------------------------------------
            note_widths: dict[float, list[Note]] = {}
            for note_id in section.note_ids:
                note = self.noteHeightCalculator.note_objects[note_id]
                if note.width not in note_widths:
                    note_widths[note.width] = []
                note_widths[note.width].append(note)

            max_width = max(note_widths)
            x = 0
            for note_width in sorted(note_widths)[::-1]:
                # We need to align it to the right but without wasting the time of removing the last translate
                group.add(Translate(max_width - note_width - x, 0, 0))
                x = max_width - note_width
                for note in note_widths[note_width]:
                    group.add(note.canvas)
            group.add(Translate(max_width - x, 0, 0))  # The rest of the heads so wide enough for next section

            # Stems ------------------------------------------
            lowest_y_id = min(section.note_ids, key=lambda x: self.noteHeightCalculator.note_objects[x].note_level)
            stem = Line(width=stem_width)
            updater = lambda *_: self.update_stem_pos(stem, lowest_y_id)
            self.noteHeightCalculator.note_objects[lowest_y_id].bind(y=updater)
            self.bind(stem_top=updater)
            updater()  # Incase the binding doesn't immediately run
            group.add(stem)

            # Return info ------------------------------------------
            width = max_width

        return group, width


    def update_stem_pos(self, stem: Line, note_id):
        note = self.noteHeightCalculator.note_objects[note_id]
        stem.points = 0, note.y + note.stem_connection_offset, 0, self.stem_top
        stem.flag_update()

    def update_bar_width(self, index):
        bar_group = self.bar_canvas.children[index].children[1]
        after_flags_group = self.bar_canvas.children[index].children[3]
        special_flags_group = self.bar_canvas.children[index].children[4]
        translate = self.bar_canvas.children[index].children[5]
        for bar in bar_group.children:
            if isinstance(bar, Line):  # Do it with if as there are also bind textures and stuff.
                bar.points[2] = self.section_widths[index]
            bar.flag_update()
        for after_flags in after_flags_group.children:
            if isinstance(after_flags, Line):
                after_flags.points[0] = self.section_widths[index] - flag_length
                after_flags.points[2] = self.section_widths[index]
            after_flags.flag_update()
        for special_flags in special_flags_group.children:
            if isinstance(special_flags, Line):
                special_flags.points[0] = self.section_widths[index]
                special_flags.points[2] = self.section_widths[index] + slanted_flag_length
            special_flags.flag_update()
        translate.x = self.section_widths[index]
