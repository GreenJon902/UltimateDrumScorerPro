import math
from typing import Optional

from kivy.clock import Clock
from kivy.graphics import Color, Line, Canvas
from kivy.properties import ObjectProperty, NumericProperty, AliasProperty, ReferenceListProperty
from kivy.uix.widget import Widget

from assembler.pageContent import PageContent
from assembler.pageContent.scoreSection.mutliNoteHolder import MultiNoteHolder
from betterLine import betterLine
from score import ScoreSectionStorage
from score.notes import notes, missing_major_note_level_height, bar_height, bar_width
from selfSizingBoxLayout import SelfSizingBoxLayout


def set_width(obj, width):
    obj.width = width


def set_points(obj: Line, points):
    obj.points = points


class ScoreSection(PageContent):
    score: ScoreSectionStorage = ObjectProperty(defaultvalue=ScoreSectionStorage())
    max_bar_height: float = NumericProperty()
    _old_score: Optional[ScoreSectionStorage] = None

    container: SelfSizingBoxLayout
    bar_container: Canvas  # Also has stems
    update = None

    def __init__(self, *args, **kwargs):
        self.update = Clock.create_trigger(self._update, -1)
        self.container = SelfSizingBoxLayout(orientation="horizontal", anchor="highest", size_hint=(None, None))
        self.bar_container = Canvas()

        PageContent.__init__(self, *args, **kwargs)

        self.bind(score=self.do_size)
        self.container.bind(size=self.do_size)

        self.add_widget(self.container)
        self.canvas.add(self.bar_container)
        self.on_score(self, self.score)

    def on_score(self, _, value):
        if self._old_score is not None:
            self._old_score.unbind_all(self.update)

        self._old_score = value
        value.bind_all(self.update)

        self.update()

    def do_size(self, _, _2):
        self.size = self.container.width, self.container.height + self.max_bar_height

    def _update(self, *_):
        print(f"Redrawing {self}")
        self.container.clear_widgets()
        self.bar_container.clear()
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
        max_bar_height = 0

        for section in self.score.sections:
            note_container = MultiNoteHolder()  # Note heads ----
            for note_id in section.note_ids:
                note = notes[note_id]()
                note.height = note_level_ys[note.note_level] + note.drawing_height
                note_container.add_widget(note)
            self.container.add_widget(note_container, index=len(self.container.children))



            if section.delta_bars > 0:  # Adding bars ----
                for n in range(section.delta_bars):
                    bar_start_widgets.append(note_container)


            if section.delta_bars < 0:  # Removing Bars ----
                for n in range(section.delta_bars * -1):
                    if not len(bar_start_widgets) > 0:
                        print(f"TRIED TO DRAW BAR THAT HASN'T STARTED - {bar_start_widgets}")
                    else:
                        if len(bar_start_widgets) * bar_height > max_bar_height:
                            max_bar_height = len(bar_start_widgets) * bar_height
                        widget = bar_start_widgets.pop(-1)
                        y = len(bar_start_widgets) * bar_height
                        self.bar_container.add(
                            betterLine(
                                widget, ("right", "top"), (0, y + bar_height / 2), 0, 0, 0, 0,
                                note_container, ("right", "top"), (0, y + bar_height / 2), 0, 0, 0, 0,
                                bar_width
                            )
                        )
        if len(bar_start_widgets) > 0:
            print(f"STILL HAS BARS LEFT TO DRAW - {bar_start_widgets}")
        self.max_bar_height = max_bar_height
