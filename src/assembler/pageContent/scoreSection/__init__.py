import math
from typing import Optional

from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

from assembler.pageContent import PageContent
from score.bar import Bar
from assembler.pageContent.scoreSection.multiBarHolder import MultiBarHolder
from assembler.pageContent.scoreSection.mutliNoteHolder import MultiNoteHolder
from score import ScoreSectionStorage
from score.notes import notes, missing_major_note_level_height
from selfSizingBoxLayout import SelfSizingBoxLayout


def set_width(obj, width, doprint=False):
    obj.width = width
    if doprint:
        print(width, doprint, doprint.children)


def set_points(obj: Line, points):
    obj.points = points


class ScoreSection(PageContent):
    score: ScoreSectionStorage = ObjectProperty(defaultvalue=ScoreSectionStorage())
    _old_score: Optional[ScoreSectionStorage] = None

    container: SelfSizingBoxLayout  # Holes everything
    bottomContainer: SelfSizingBoxLayout  # Note heads and decoration
    topContainer: SelfSizingBoxLayout  # Bars
    update = None

    def __init__(self, *args, **kwargs):
        self.update = Clock.create_trigger(self._update, -1)
        self.container = SelfSizingBoxLayout(orientation="vertical")
        self.bottomContainer = SelfSizingBoxLayout(orientation="horizontal", anchor="highest")
        self.topContainer = SelfSizingBoxLayout(orientation="horizontal", anchor="lowest")
        self.container.add_widget(self.topContainer)
        self.container.add_widget(self.bottomContainer)

        PageContent.__init__(self, *args, **kwargs)

        self.container.bind(size=self.on_container_size)

        self.add_widget(self.container)
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
        note_objs = [notes[note_id]() for section in self.score.sections for note_id in section.note_ids]

        #  Get note levels as y levels ---------------------------------------------------------------------------------
        note_level_heights = {}  # Biggest height at each note_level
        major_note_levels = set()  # Integer part of note levels
        for note in note_objs:
            if note.note_level not in note_level_heights:
                note_level_heights[note.note_level] = note.drawing_height
            elif note.drawing_height > note_level_heights[note.note_level]:
                note_level_heights[note.note_level] = note.drawing_height
            major_note_levels.add(math.floor(note.note_level))
        max_note_level = max(note_level_heights)
        missing_levels = major_note_levels.symmetric_difference(range(1, math.floor(max_note_level) + 1))
        note_level_heights.update({level: missing_major_note_level_height for level in missing_levels})

        y = 0
        note_level_ys = {}
        for note_level in sorted(note_level_heights.keys(), reverse=True):
            note_level_ys[note_level] = y
            y += note_level_heights[note_level]

        #  Draw --------------------------------------------------------------------------------------------------
        reversed_sections = self.score.sections[::-1]
        for i in range(len(reversed_sections) + 1):
            if i < len(reversed_sections):
                section = reversed_sections[i]
            else:
                section = None
            if i - 1 >= 0:
                last_section = reversed_sections[i - 1]
            else:
                last_section = None

            if section is not None:  # Heads
                note_container = MultiNoteHolder()
                for note_id in section.note_ids:
                    note = notes[note_id]()
                    note.height = note_level_ys[note.note_level] + note.drawing_height
                    note_container.add_widget(note)
                self.bottomContainer.add_widget(note_container, index=len(self.bottomContainer.children))
            else:
                note_container = MultiNoteHolder()
                note_container.add_widget(Widget(width=5, height=5))  # Need a size so bars show
                self.bottomContainer.add_widget(note_container, index=len(self.bottomContainer.children))

            if i != 0:
                assert last_section is not None
                bar_container = MultiBarHolder(width=note_container.width)  # Bars
                note_container.bind(width=lambda *args, bar_container_=bar_container, note_container_=note_container:
                                    set_width(bar_container_, note_container_.width))
                for n in range(last_section.bars):
                    bar_container.add_widget(Bar())
                self.topContainer.add_widget(bar_container, index=len(self.bottomContainer.children))

            else:
                bar_container = MultiBarHolder(width=note_container.width)  # Bars
                note_container.bind(width=lambda *args, bar_container_=bar_container, note_container_=note_container:
                                    set_width(bar_container_, note_container_.width, bar_container_))
                self.topContainer.add_widget(bar_container, index=len(self.bottomContainer.children))

