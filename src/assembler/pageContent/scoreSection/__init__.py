import math
import time
from typing import Optional

from kivy import Logger
from kivy.graphics import Line, Canvas
from kivy.properties import ObjectProperty

from argumentTrigger import ArgumentTrigger
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

    container: SelfSizingBoxLayout  # Holds everything
    bottomContainer: SelfSizingBoxLayout  # Note heads and decoration
    topContainer: SelfSizingBoxLayout  # Bars
    bar_canvas: Canvas
    stem_canvas: Canvas
    dot_canvas: Canvas
    update = None
    note_level_ys: dict[float, int]
    id_of_note_with_highest_level: Optional[int]  # So when modifying just one scoreSectionSection, we know if we need
                                                  # to do a full redraw as distance from bars needs to be updated
    max_note_level_indexes: list[int]  # Same reason as above, this stores whether the section at that index has a
                                       # note at that level

    def __init__(self, *args, **kwargs):
        self.note_level_ys = {}
        self.id_of_note_with_highest_level = None
        self.max_note_level_indexes = []

        self.update = ArgumentTrigger(self._update, -1, True)
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

        self.update("all")

    def on_container_size(self, _, value):
        self.size = value

    def _update(self, changes: list[tuple[tuple[any], dict[str, any]]]):
        Logger.info(f"ScoreSection: Updating {self} with {changes}...")
        t = time.time()

        # TODO: optimize by skipping stuff that gets overwritten (e.g. add bar before full redraw)
        for change in changes:
            change = change[0]  # We don't care about kwargs
            Logger.debug(f"ScoreSection: Changing {change}")
            if change[0] == "all":
                self.full_redraw()
            elif change[0] == "section" and change[1] == "note_ids":
                ret = self.update_heads_at(self.score.index(change[2]))
                if ret == "did_full":
                    Logger.debug("ScoreSection: Ended up having to do a full redraw so discarding any other changes")
                    break
            else:
                raise NotImplementedError(f"Score section doesn't know how to change {change}")

        Logger.info(f"ScoreSection: {time.time() - t}s elapsed!")


    def full_redraw(self):
        self.id_of_note_with_highest_level = None
        self.max_note_level_indexes.clear()

        self.bottomContainer.clear_widgets()
        self.topContainer.clear_widgets()
        self.bar_canvas.clear()
        self.stem_canvas.clear()
        note_ids = set()
        for section in self.score:
            note_ids.update(section.note_ids)
        note_objs = {note_id: notes[note_id]() for note_id in note_ids}

        #  Get note levels as y levels ---------------------------------------------------------------------------------
        note_level_heights = {}  # Height at each note_level
        major_note_levels = set()  # Integer part of note levels
        for note_id, note in note_objs.items():
            note_level_heights[note.note_level] = note.drawing_height
            if note.drawing_height == max(note_level_heights.values()):
                self.id_of_note_with_highest_level = note_id
            major_note_levels.add(math.floor(note.note_level))
        if len(note_level_heights) != 0:
            max_note_level = max(note_level_heights.keys())
        else:
            max_note_level = 1
        missing_levels = major_note_levels.symmetric_difference(range(1, math.floor(max_note_level) + 1))
        note_level_heights.update({level: missing_major_note_level_height for level in missing_levels})

        y = 0
        note_level_ys = {}
        for note_level in sorted(note_level_heights.keys(), reverse=True):
            note_level_ys[note_level] = y
            y += note_level_heights[note_level]
        self.note_level_ys = note_level_ys

        #  Draw --------------------------------------------------------------------------------------------------
        bar_start_widgets = []
        next_flags = []

        for i, section in enumerate(self.score):
            note_container = MultiNoteHolder()
            bar_container = MultiBarHolder(note_container)
            self.bottomContainer.add_widget(note_container, index=len(self.bottomContainer.children))
            self.topContainer.add_widget(bar_container, index=len(self.topContainer.children))

            # Heads ----------------------------------------------
            for note_id in section.note_ids:
                note = notes[note_id]()
                note.height = note_level_ys[note.note_level] + note.drawing_height
                note_container.add_widget(note)

                if note.note_level == max_note_level:
                    self.max_note_level_indexes.append(i)


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
                        Logger.warning(f"ScoreSection: TRIED TO DRAW BAR THAT HASN'T STARTED - {bar_start_widgets}")
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
            Logger.warning(f"ScoreSection: STILL HAS BARS LEFT TO DRAW - {bar_start_widgets}")

        if len(next_flags) > 0:
            note_container = MultiNoteHolder()
            bar_container = MultiBarHolder(note_container)
            self.bottomContainer.add_widget(note_container, index=len(self.bottomContainer.children))
            self.topContainer.add_widget(bar_container, index=len(self.topContainer.children))

            for bar in next_flags:
                bar_container.add_widget(bar)
                self.bar_canvas.add(draw_slanted_flag(bar))


    def update_heads_at(self, index):
        section = self.score[index]
        note_container: MultiNoteHolder = self.bottomContainer.children[-index]
        note_container.clear_widgets()

        if (self.id_of_note_with_highest_level not in section.note_ids) and (index in self.max_note_level_indexes):
            self.max_note_level_indexes.remove(index)
            if len(self.max_note_level_indexes) == 0:
                Logger.debug("ScoreSection: Highest note is completely gone so will full redraw...")
                # We have removed the last note head that's at the highest position, we now need to redraw everything as
                # otherwise distance from bars and flag would be too great
                self.full_redraw()
                return "did_full"


        for note_id in section.note_ids:
            note = notes[note_id]()
            if note.note_level not in self.note_level_ys:
                Logger.debug("ScoreSection: Need new note level y so will full redraw...")
                # If we don't have a y level yet then everything needs to be redrawn
                self.full_redraw()
                return "did_full"
            note.height = self.note_level_ys[note.note_level] + note.drawing_height
            note_container.add_widget(note)
