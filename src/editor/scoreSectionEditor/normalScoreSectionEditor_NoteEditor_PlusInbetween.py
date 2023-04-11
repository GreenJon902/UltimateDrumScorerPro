import time
from typing import Optional

from kivy import Logger
from kivy.clock import Clock
from kivy.input import MotionEvent
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from argumentTrigger import ArgumentTrigger
from assembler.pageContent.scoreSection import NoteHeightCalculator
from editor.scoreSectionEditor.normalScoreSectioneditor import NormalScoreSectionEditor_NoteEditor
from score import ScoreSectionStorage, ScoreSectionSectionStorage, fix_and_get_normal_editor_note_ids
from score.notes import notes, Note
from selfSizingBoxLayout import SelfSizingBoxLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor_NoteEditor_PlusInbetween.kv")


# noinspection PyPep8Naming
class NormalScoreSectionEditor_NoteEditor_PlusInbetween(NormalScoreSectionEditor_NoteEditor):
    score: ScoreSectionStorage = ObjectProperty(defaultvalue=ScoreSectionStorage())
    _old_score: Optional[ScoreSectionStorage] = None

    update = None
    update_size = None

    noteHeightCalculator: NoteHeightCalculator
    note_holder: SelfSizingBoxLayout = ObjectProperty()

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        self.update = ArgumentTrigger(self._update, -1, True)
        self.update_size = Clock.create_trigger(self._update_size, -1)
        self.noteHeightCalculator = NoteHeightCalculator()
        NormalScoreSectionEditor_NoteEditor.__init__(self, **kwargs)

        self.on_score(self, self.score)


    def _update_size(self, _):
        pass

    def on_score(self, _, value):
        if self._old_score is not None:
            self._old_score.unbind_all(self.update)

        self._old_score = value
        value.bind_all(self.update)
        self.noteHeightCalculator.score = value

        self.update("all")

    def _update(self, changes: list[tuple[tuple[any], dict[str, any]]]):
        Logger.info(f"NSSE_NE_PlusInbetween: Updating {self} with {changes}...")
        t = time.time()

        # TODO: optimize by skipping stuff that gets overwritten (e.g. add bar before full redraw)
        for change in changes:
            change = change[0]  # We don't care about kwargs
            Logger.debug(f"NSSE_NE_PlusInbetween: Changing {change}")

            if change[0] == "all" or (change[0] == "storage" and change[1] == "set"):
                self.full_redraw()

        Logger.info(f"NSSE_NE_PlusInbetween: {time.time() - t}s elapsed!")

    def full_redraw(self):
        note_ids = fix_and_get_normal_editor_note_ids(self.score_section_instance.score)
        ordered_note_types = sorted([(note_id, notes[note_id]) for note_id in note_ids],
                                    key=lambda x: x[1]().note_level,
                                    reverse=True)  # Reverse cause of how they get added

        self.note_holder.clear_widgets()
        for i in range(len(self.score_section_instance.score)):
            section = self.score_section_instance.score[i]
            holder = SelfSizingBoxLayout(orientation="vertical")
            for (note_id, note_type) in ordered_note_types:
                note: Note = note_type()
                note.color[3] = 1 if note_id in section.note_ids else 0.1
                note.bind(on_touch_down=lambda _, touch, note_=note, section_=section, note_id_=note_id:
                          note_clicked(note_, touch, section_, note_id_))
                holder.add_widget(note)
            self.note_holder.add_widget(holder, index=len(self.note_holder.children))


def note_clicked(note: Note, touch: MotionEvent, section: ScoreSectionSectionStorage, note_id: int):
    if note.collide_point(*touch.pos):
        if note_id in section.note_ids:
            section.note_ids.remove(note_id)
        else:
            section.note_ids.append(note_id)

        note.color[3] = 1 if note_id in section.note_ids else 0.1
        return True
