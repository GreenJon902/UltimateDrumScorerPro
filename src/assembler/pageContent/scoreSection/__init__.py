import time
from typing import Optional

from kivy import Logger
from kivy.graphics import Line, Canvas, PushMatrix, PopMatrix, Translate, InstructionGroup
from kivy.properties import ObjectProperty

from argumentTrigger import ArgumentTrigger
from assembler.pageContent import PageContent
from assembler.pageContent.scoreSection.bars import MultiBarHolder, Bar, draw_bar
from assembler.pageContent.scoreSection.dots import draw_dots
from assembler.pageContent.scoreSection.flags import draw_before_flag, draw_after_flag, draw_slanted_flag
from assembler.pageContent.scoreSection.mutliNoteHolder import MultiNoteHolder
from assembler.pageContent.scoreSection.noteHeightCalculator import NoteHeightCalculator
from assembler.pageContent.scoreSection.stems import draw_stem
from score import ScoreSectionStorage
from score.notes import Note


def set_width(obj, width):
    obj.width = width


def set_points(obj: Line, points):
    obj.points = points


class ScoreSection(PageContent):
    score: ScoreSectionStorage = ObjectProperty(defaultvalue=ScoreSectionStorage())
    _old_score: Optional[ScoreSectionStorage] = None

    head_canvas: Canvas
    head_canvas_container: Canvas

    update = None

    noteHeightCalculator: NoteHeightCalculator

    def __init__(self, *args, **kwargs):
        self.update = ArgumentTrigger(self._update, -1, True)
        self.noteHeightCalculator = NoteHeightCalculator()

        self.head_canvas_container = Canvas()
        self.head_canvas = Canvas()
        self.head_canvas_container.add(PushMatrix())
        self.head_canvas_container.add(self.head_canvas)
        self.head_canvas_container.add(PopMatrix())

        PageContent.__init__(self, *args, **kwargs)

        self.canvas.add(self.head_canvas_container)
        self.on_score(self, self.score)

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
                self.update_section(self.score.index(change[2]))
                pass
            else:
                raise NotImplementedError(f"Score section doesn't know how to change {change}")

        Logger.info(f"ScoreSection: {time.time() - t}s elapsed!")

    def full_redraw(self):
        self.head_canvas.clear()
        for i in range(len(self.score)):
            self.add_section(i)

    def add_section(self, index):
        self.head_canvas.insert(index, self._make_section_group(index))

    def update_section(self, index):
        self.head_canvas.children[index] = self._make_section_group(index)
        self.head_canvas.flag_update()

    def _make_section_group(self, index):
        self.noteHeightCalculator.update()

        section = self.score[index]
        group = InstructionGroup()

        if len(section.note_ids) != 0:
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

        return group
