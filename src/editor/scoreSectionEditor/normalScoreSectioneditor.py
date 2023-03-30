from kivy.lang import Builder
from kivy.metrics import mm
from kivy.properties import ObjectProperty, Clock, OptionProperty
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.widget import Widget

from assembler.pageContent.scoreSection import ScoreSection
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
        self.score_section_instance.score.bind_all(self.trigger_update_labels)

        self.trigger_update_labels()
        self.trigger_refresh_all_notes()

    def _update_labels(self, *args):
        note_ids = set(self.score_section_instance.score.normal_editor_note_ids)
        note_ids.update({note_id for section in self.score_section_instance.score.sections
                         for note_id in section.note_ids})
        #  We add in any that may have been missed but are in the score, use set so no duplicates

        ordered_note_types = sorted([notes[note_id] for note_id in note_ids], key=lambda x: x().note_level,
                                    reverse=True)  # Reverse cause of how they get added

        self.label_holder.clear_widgets()
        for note_type in ordered_note_types:
            note = note_type()
            self.label_holder.add_widget(NoteNameLabel(text=str(note.name), height=mm(note.drawing_height)))

    def _refresh_all_notes(self, *args):
        note_ids = {note_id for section in self.score_section_instance.score.sections for note_id in section.note_ids}
        ordered_note_types = sorted([(note_id, notes[note_id]) for note_id in note_ids],
                                    key=lambda x: x[1]().note_level,
                                    reverse=True)  # Reverse cause of how they get added
        for section in self.score_section_instance.score.sections:
            holder = SelfSizingBoxLayout(orientation="vertical")
            for (note_id, note_type) in ordered_note_types:
                note: Note = note_type()
                note.height = note.drawing_height
                note.color[3] = 1 if note_id in section.note_ids else 0.1
                holder.add_widget(note)
            self.note_holder.add_widget(holder, index=len(self.note_holder.container.children))


class NoteNameLabel(Label):
    pass


class ZoomedLayout(Widget):
    container: SelfSizingBoxLayout = ObjectProperty()
    orientation = OptionProperty("horizontal", options=("horizontal", "vertical"))
    anchor = OptionProperty("middle", options=("lowest", "middle", "highest"))

    def add_widget(self, widget, *args, **kwargs):
        if len(self.children) != 0:
            self.children[0].add_widget(widget, *args, **kwargs)
        else:
            Widget.add_widget(self, widget, *args, **kwargs)
