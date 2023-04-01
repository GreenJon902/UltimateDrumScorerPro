import math
import time
from typing import Optional

from kivy.clock import Clock
from kivy.graphics import Line, Canvas
from kivy.properties import ObjectProperty

from assembler.pageContent import PageContent
from assembler.pageContent.scoreSection.bars import MultiBarHolder, Bar, draw_bar
from assembler.pageContent.scoreSection.dots import draw_dots
from assembler.pageContent.scoreSection.flags import draw_before_flag, draw_after_flag, draw_slanted_flag
from assembler.pageContent.scoreSection.mutliNoteHolder import MultiNoteHolder
from assembler.pageContent.scoreSection.stems import draw_stem
from score import ScoreSectionStorage
from score.notes import notes, missing_major_note_level_height
from selfSizingBoxLayout import SelfSizingBoxLayout


def set_width(obj, width):
    obj.width = width


def set_points(obj: Line, points):
    obj.points = points


class ScoreSection(PageContent):
    score: ScoreSectionStorage = ObjectProperty(defaultvalue=ScoreSectionStorage())
    _old_score: Optional[ScoreSectionStorage] = None
    _old_section_count = None

    container: SelfSizingBoxLayout  # Holds everything
    bottomContainer: SelfSizingBoxLayout  # Note heads and decoration
    topContainer: SelfSizingBoxLayout  # Bars
    bar_canvas: Canvas
    stem_canvas: Canvas
    dot_canvas: Canvas
    update = None

    def __init__(self, *args, **kwargs):
        self.update = Clock.create_trigger(self._update, -1)
        self.container = SelfSizingBoxLayout(orientation="vertical")
        self.bottomContainer = SelfSizingBoxLayout(orientation="horizontal", anchor="highest")
        self.topContainer = SelfSizingBoxLayout(orientation="horizontal", anchor="highest")
        self.bar_canvas = Canvas()
        self.stem_canvas = Canvas()
        self.dot_canvas = Canvas()
        self.container.add_widget(self.topContainer)
        self.container.add_widget(self.bottomContainer)

        PageContent.__init__(self, *args, **kwargs)

        self.container.bind(size=self.on_container_size)

        self.add_widget(self.container)
        self.canvas.add(self.bar_canvas)
        self.canvas.add(self.stem_canvas)
        self.canvas.add(self.dot_canvas)
        self.on_score(self, self.score)

    def on_score(self, _, value):
        if self._old_score is not None:
            self._old_score.unbind_all(self.update)

        self._old_score = value
        value.bind_all(self.update)

        self.update()

    def on_container_size(self, _, value):
        self.size = value

    def _update(self, *_):
        print(f"Redrawing {self}")
        self.bottomContainer.clear_widgets()
        self.topContainer.clear_widgets()
        self.bar_canvas.clear()
        self.stem_canvas.clear()
        note_objs = [notes[note_id]() for section in self.score for note_id in section.note_ids]

        #  Get note levels as y levels ---------------------------------------------------------------------------------
        note_level_heights = {}  # Biggest height at each note_level
        major_note_levels = set()  # Integer part of note levels
        for note in note_objs:
            if note.note_level not in note_level_heights:
                note_level_heights[note.note_level] = note.drawing_height
            elif note.drawing_height > note_level_heights[note.note_level]:
                note_level_heights[note.note_level] = note.drawing_height
            major_note_levels.add(math.floor(note.note_level))
        if len(note_level_heights) != 0:
            max_note_level = max(note_level_heights)
        else:
            max_note_level = 1
        missing_levels = major_note_levels.symmetric_difference(range(1, math.floor(max_note_level) + 1))
        note_level_heights.update({level: missing_major_note_level_height for level in missing_levels})

        y = 0
        note_level_ys = {}
        for note_level in sorted(note_level_heights.keys(), reverse=True):
            note_level_ys[note_level] = y
            y += note_level_heights[note_level]

        #  Draw --------------------------------------------------------------------------------------------------
        bar_start_widgets = []
        next_flags = []

        self._old_section_count = len(self.score)
        for section in self.score:
            note_container = MultiNoteHolder()
            bar_container = MultiBarHolder(note_container)
            self.bottomContainer.add_widget(note_container, index=len(self.bottomContainer.children))
            self.topContainer.add_widget(bar_container, index=len(self.topContainer.children))

            # Heads ----------------------------------------------
            for note_id in section.note_ids:
                note = notes[note_id]()
                note.height = note_level_ys[note.note_level] + note.drawing_height
                note_container.add_widget(note)


            # Dots ----------------------------------------------
            for child in note_container.children:
                self.dot_canvas.add(draw_dots(section.dots, child))


            # Bars ----------------------------------------------
            for n in range(len(bar_start_widgets)):  # Retaining bars
                bar = Bar()
                bar_container.add_widget(bar)

            if section.delta_bars > 0:  # Adding bars
                for n in range(section.delta_bars):
                    bar = Bar()
                    bar_container.add_widget(bar)
                    bar_start_widgets.append(bar)

            if section.delta_bars < 0:  # Removing Bars
                for n in range(section.delta_bars * -1):
                    if not len(bar_start_widgets) > 0:
                        print(f"TRIED TO DRAW BAR THAT HASN'T STARTED - {bar_start_widgets}")
                    else:
                        old_bar = bar_start_widgets.pop(-1)
                        new_bar = bar_container.children[n]
                        self.bar_canvas.add(draw_bar(old_bar, new_bar))


            # Flags ----------------------------------------------
            for n in range(section.before_flags):  # Before stem
                bar = Bar()
                bar_container.add_widget(bar)
                self.bar_canvas.add(draw_before_flag(bar))

            for bar in next_flags:   # Last stem's after
                bar_container.add_widget(bar)
                self.bar_canvas.add(draw_after_flag(bar))
            next_flags.clear()

            for n in range(section.after_flags):  # Prepare this stem's after
                bar = Bar()
                next_flags.append(bar)


            # Stems ----------------------------------------------
            self.stem_canvas.add(draw_stem(note_container, bar_container))


        if len(bar_start_widgets) > 0:
            print(f"STILL HAS BARS LEFT TO DRAW - {bar_start_widgets}")

        if len(next_flags) > 0:
            note_container = MultiNoteHolder()
            bar_container = MultiBarHolder(note_container)
            self.bottomContainer.add_widget(note_container, index=len(self.bottomContainer.children))
            self.topContainer.add_widget(bar_container, index=len(self.topContainer.children))

            for bar in next_flags:
                bar_container.add_widget(bar)
                self.bar_canvas.add(draw_slanted_flag(bar))
