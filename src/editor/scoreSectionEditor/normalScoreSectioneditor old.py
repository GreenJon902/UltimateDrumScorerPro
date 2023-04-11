from kivy.input import MotionEvent
from kivy.lang import Builder
from kivy.metrics import mm
from kivy.properties import ObjectProperty, Clock
from kivy.uix.tabbedpanel import TabbedPanelItem

from assembler.pageContent.scoreSection import ScoreSection
from score import ScoreSectionSectionStorage
from score.notes import notes, Note
from selfSizingBoxLayout import SelfSizingBoxLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor.kv")


class NormalScoreSectionEditor(TabbedPanelItem):
    score_section_instance: ScoreSection

    trigger_update_labels = None
    trigger_refresh_all_notes = None

    label_holder: SelfSizingBoxLayout = ObjectProperty()
    note_holder: SelfSizingBoxLayout = ObjectProperty()

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        self.trigger_update_labels = Clock.create_trigger(self._update_labels, 0)
        self.trigger_refresh_all_notes = Clock.create_trigger(self._refresh_all_notes, 0)
        TabbedPanelItem.__init__(self, **kwargs)

        self.score_section_instance.score.bind(normal_editor_note_ids=self.trigger_update_labels)
        self.score_section_instance.score.bind(normal_editor_note_ids=self._refresh_all_notes)
        self.score_section_instance.score.bind_all(self.trigger_update_labels)

        self.trigger_update_labels()
        self.trigger_refresh_all_notes()


    def fix_and_get_normal_editor_note_ids(self):
        #  We add in any note_ids that are present but not allowed to be edited, use set so no duplicates
        note_ids = set(self.score_section_instance.score.normal_editor_note_ids)
        note_ids.update({note_id for section in self.score_section_instance.score for note_id in section.note_ids})
        self.score_section_instance.score.normal_editor_note_ids = note_ids
        return note_ids

    def _update_labels(self, *args):
        note_ids = self.fix_and_get_normal_editor_note_ids()
        ordered_note_types = sorted([notes[note_id] for note_id in note_ids], key=lambda x: x().note_level,
                                    reverse=True)  # Reverse cause of how they get added

        self.label_holder.clear_widgets()
        for note_type in ordered_note_types:
            note = note_type()
            self.label_holder.add_widget(NoteNameLabel(text=str(note.name), height=mm(note.height)))

    def _refresh_all_notes(self, *args):
        note_ids = self.fix_and_get_normal_editor_note_ids()
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
            self.note_holder.add_widget(holder, index=self.note_holder.n_children())



def note_clicked(note: Note, touch: MotionEvent, section: ScoreSectionSectionStorage, note_id: int):
    if note.collide_point(*touch.pos):
        if note_id in section.note_ids:
            section.note_ids.remove(note_id)
        else:
            section.note_ids.append(note_id)

        note.color[3] = 1 if note_id in section.note_ids else 0.1
        return True


