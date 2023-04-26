import time

from kivy import Logger
from kivy.clock import Clock
from kivy.graphics import Ellipse, Line, InstructionGroup, Canvas, Translate, PushMatrix, PopMatrix
from kivy.lang import Builder

from argumentTrigger import ArgumentTrigger
from assembler.pageContent.scoreSection import ScoreSection
from editor.scoreSectionEditor.normalScoreSectioneditor import NormalScoreSectionEditor_NoteEditor
from score import fix_and_get_normal_editor_note_ids
from score.notes import notes, Note, dot_radius, dot_spacing, bar_width, flag_length, slanted_flag_length, \
    slanted_flag_height_offset, dot_head_spacing
from selfSizingBoxLayout import SelfSizingBoxLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor_NoteEditor_PlusInbetween.kv")


class Drawer:
    def __init__(self, item_translate, item, section_translate):
        self.canvas_container = Canvas()
        self.canvas = Canvas()
        self.canvas_translate = Translate()
        self.canvas_container.add(PushMatrix())
        self.canvas_container.add(self.canvas_translate)
        self.canvas_container.add(self.canvas)
        self.canvas_container.add(PopMatrix())

        self.item_translate = item_translate
        self.item = item
        self.section_translate = section_translate

    def add_to(self, canvas):
        canvas.add(self.canvas_container)

    def new_section(self, index):
        canvas = Canvas()
        self.canvas.insert(index, canvas)

    def update(self, index, amount):
        section_before_bar_canvas: Canvas = self.canvas.children[index]
        section_before_bar_canvas.clear()
        section_before_bar_canvas.children.clear()

        if amount == 0:
            section_before_bar_canvas.opacity = 0.3
            section_before_bar_canvas.add(self.item)
            section_before_bar_canvas.add(self.section_translate)
        else:
            section_before_bar_canvas.opacity = 1
            section_before_bar_canvas.add(PushMatrix())
            for i in range(amount):
                section_before_bar_canvas.add(self.item)
                section_before_bar_canvas.add(self.item_translate)
            section_before_bar_canvas.add(PopMatrix())
            section_before_bar_canvas.add(self.section_translate)

    def clear(self):
        self.canvas.clear()

    def remove(self, index):
        self.canvas.remove(self.canvas.children[index])


# noinspection PyPep8Naming
class NormalScoreSectionEditor_NoteEditor_PlusInbetween(NormalScoreSectionEditor_NoteEditor):
    update = None
    update_size = None

    head_translate: Translate
    head_canvas: Canvas
    head_canvas_container: Canvas
    head_canvas_translate: Translate

    score_section_instance: ScoreSection
    note_head_canvases: dict[int, list[Canvas]]  # For opacity

    note_objects: dict[int, Note]
    note_object_holder: SelfSizingBoxLayout

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        self.note_head_canvases = {i: [] for i in range(len(notes))}
        self.update = ArgumentTrigger(self._update, -1, True)
        self.update_size = Clock.create_trigger(self._update_size, -1)

        self.head_canvas_container = Canvas()
        self.head_canvas = Canvas()
        self.head_canvas_container.add(PushMatrix())
        self.head_canvas_container.add(self.head_canvas)
        self.head_canvas_container.add(PopMatrix())

        self.section_translate = Translate()
        self.full_bar_line = Line(points=[0, 4/2, 0, 4/2], width=bar_width)
        self.before_bar_line = Line(points=[0, 4/2, flag_length, 4/2], width=bar_width)
        self.after_bar_line = Line(points=[0, 4/2, 0, 4/2], width=bar_width)
        self.slanted_bar_line = Line(points=[0, 0, slanted_flag_length, -slanted_flag_height_offset], width=bar_width)
        self.dot = Ellipse(pos=[0, 0], size=[dot_radius * 2, dot_radius * 2])
        self.full_bar_translate = Translate(0, 2, 0)  # Todo: Actual value
        self.before_bar_translate = Translate(0, 2, 0)  # Todo: Actual value
        self.after_bar_translate = Translate(0, 2, 0)  # Todo: Actual value
        self.slanted_bar_translate = Translate(0, 2, 0)  # Todo: Actual value
        self.dots_translate = Translate(dot_spacing, 0, 0)  # Todo: Actual value


        self.full_bar_drawer = Drawer(self.full_bar_translate, self.full_bar_line, self.section_translate)
        self.before_bar_drawer = Drawer(self.before_bar_translate, self.before_bar_line, self.section_translate)
        self.after_bar_drawer = Drawer(self.after_bar_translate, self.after_bar_line, self.section_translate)
        self.slanted_bar_drawer = Drawer(self.slanted_bar_translate, self.slanted_bar_line, self.section_translate)
        self.dots_drawer = Drawer(self.dots_translate, self.dot, self.section_translate)


        self.note_objects = {}
        self.note_object_holder = SelfSizingBoxLayout(anchor="highest", orientation="vertical")
        for (note_id, note_type) in sorted(notes.items(), key=lambda x: x[1]().note_level, reverse=True):
            note: Note = note_type()
            self.note_object_holder.add_widget(note)
            self.note_objects[note_id] = note
            note.opacity = 1

        NormalScoreSectionEditor_NoteEditor.__init__(self, **kwargs)

        for note in self.score_section_instance.noteHeightCalculator.note_objects.values():
            note.fbind("y", self.update_size)
        self.update_size()

        self.score_section_instance.score.bind_all(self.update)
        self.note_object_holder.bind(height=self.update_size)
        self.canvas.add(self.head_canvas_container)
        self.full_bar_drawer.add_to(self.canvas)
        self.before_bar_drawer.add_to(self.canvas)
        self.after_bar_drawer.add_to(self.canvas)
        self.slanted_bar_drawer.add_to(self.canvas)
        self.dots_drawer.add_to(self.canvas)
        self.update("all")

    def _update_size(self, _):
        full_bar_amount = max(*(section.bars for section in self.score_section_instance.score), 2)  # Grey bars
        before_bar_amount = max(*(section.before_flags for section in self.score_section_instance.score), 2)
        after_bar_amount = max(*(section.after_flags for section in self.score_section_instance.score), 0)

        self.slanted_bar_drawer.canvas_translate.x = self.section_translate.x * len(self.score_section_instance.score)

        y = self.note_object_holder.height + dot_head_spacing
        self.dots_drawer.canvas_translate.y = y
        y += dot_radius * 2
        self.full_bar_drawer.canvas_translate.y = y
        y += full_bar_amount * 2
        self.before_bar_drawer.canvas_translate.y = y
        y += before_bar_amount * 2
        self.after_bar_drawer.canvas_translate.y = y
        y += after_bar_amount * 2 - (self.score_section_instance.score[-1].slanted_flags - 1) * 2
        self.slanted_bar_drawer.canvas_translate.y = y

    def _update(self, changes: list[tuple[tuple[any], dict[str, any]]]):
        Logger.info(f"NSSE_NE_PlusInbetween: Updating {self} with {changes}...")
        t = time.time()

        note_ids = fix_and_get_normal_editor_note_ids(self.score_section_instance.score)
        width = 0
        note: Note
        for i, note in self.note_objects.items():
            if i in note_ids:
                note.height = note.preferred_height
                note.opacity = 1
                if note.width > width:
                    width = note.width
            else:
                note.height = 0
                note.opacity = 0
        self.section_translate.x = width
        self.full_bar_line.points[2] = width
        self.after_bar_line.points[0] = width - flag_length
        self.after_bar_line.points[2] = width

        # TODO: optimize by skipping stuff that gets overwritten (e.g. add bar before full redraw)
        for change in changes:
            change = change[0]  # We don't care about kwargs
            Logger.debug(f"NSSE_NE_PlusInbetween: Changing {change}")

            if change[0] == "all" or (change[0] == "storage" and change[1] == "set"):
                self.full_redraw()
            elif change[0] == "storage" and change[1] == "insert":
                self.add_section(change[2])
            elif change[0] == "storage" and change[1] == "remove":
                self.remove_section(change[2])

            elif change[0] == "section" and change[1] == "note_ids":
                self.update_head_canvas_colors(self.score_section_instance.score.index(change[2]))
            elif change[0] == "section" and (change[1] == "bars"):
                self.update_section_full_bars(self.score_section_instance.score.index(change[2]))
            elif change[0] == "section" and (change[1] == "before_flags"):
                self.update_section_before_bars(self.score_section_instance.score.index(change[2]))
            elif change[0] == "section" and (change[1] == "after_flags"):
                self.update_section_after_bars(self.score_section_instance.score.index(change[2]))
            elif change[0] == "section" and (change[1] == "slanted_flags"):
                self.update_section_slanted_bars()
            elif change[0] == "section" and change[1] == "dots":
                self.update_section_dots(self.score_section_instance.score.index(change[2]))
            else:
                raise NotImplementedError(f"Score section doesn't know how to change {change}")

        Logger.info(f"NSSE_NE_PlusInbetween: {time.time() - t}s elapsed!")

    def full_redraw(self):
        self.head_canvas.clear()
        self.full_bar_drawer.clear()
        self.before_bar_drawer.clear()
        self.after_bar_drawer.clear()
        self.slanted_bar_drawer.clear()
        self.dots_drawer.clear()
        for note_id in self.note_head_canvases:
            self.note_head_canvases[note_id].clear()

        for i in range(len(self.score_section_instance.score)):
            self.add_section(i)

        self.slanted_bar_drawer.new_section(0)
        self.update_section_slanted_bars()

    def add_section(self, index):
        head_group = InstructionGroup()
        for (note_id, note_object) in self.note_objects.items():
            canvas = Canvas()
            self.note_head_canvases[note_id].insert(index, canvas)
            canvas.add(note_object.canvas)
            head_group.add(canvas)
        head_group.add(self.section_translate)
        self.head_canvas.insert(index, head_group)

        self.full_bar_drawer.new_section(index)
        self.before_bar_drawer.new_section(index)
        self.after_bar_drawer.new_section(index)
        self.dots_drawer.new_section(index)

        self.update_head_canvas_colors(index)
        self.update_section_full_bars(index)
        self.update_section_before_bars(index)
        self.update_section_after_bars(index)
        self.update_section_dots(index)

    def remove_section(self, index):
        self.head_canvas.remove(self.head_canvas.children[index])
        self.full_bar_drawer.remove(index)
        self.before_bar_drawer.remove(index)
        self.after_bar_drawer.remove(index)
        self.dots_drawer.remove(index)
        for note_id in self.note_head_canvases:
            self.note_head_canvases[note_id].pop(index)

        self.update_size()

    def update_head_canvas_colors(self, index):
        for note_id in self.note_head_canvases:
            if note_id in self.score_section_instance.score[index].note_ids:
                self.note_head_canvases[note_id][index].opacity = 1
            else:
                self.note_head_canvases[note_id][index].opacity = 0.3

    def update_section_full_bars(self, index):
        self.full_bar_drawer.update(index, self.score_section_instance.score[index].bars)
        self.update_size()

    def update_section_before_bars(self, index):
        self.before_bar_drawer.update(index, self.score_section_instance.score[index].before_flags)
        self.update_size()

    def update_section_after_bars(self, index):
        self.after_bar_drawer.update(index, self.score_section_instance.score[index].after_flags)
        self.update_size()

    def update_section_dots(self, index):
        self.dots_drawer.update(index, self.score_section_instance.score[index].dots)
        self.update_size()

    def update_section_slanted_bars(self):
        self.after_bar_drawer.update(0, self.score_section_instance.score[-1].after_flags)
        self.update_size()
