from kivy.input import MotionEvent
from kivy.lang import Builder
from kivy.metrics import mm
from kivy.properties import ObjectProperty, Clock, OptionProperty
from kivy.uix.label import Label
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.widget import Widget

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
            self.label_holder.add_widget(NoteNameLabel(text=str(note.name), height=mm(note.drawing_height)))

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
                note.height = note.drawing_height
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


class NoteNameLabel(Label):
    pass


class ZoomedLayout(ScatterLayout):
    container: SelfSizingBoxLayout = ObjectProperty()
    orientation = OptionProperty("horizontal", options=("horizontal", "vertical"))
    anchor = OptionProperty("middle", options=("lowest", "middle", "highest"))

    def make_container(self, *args, **kwargs):
        self.container = SelfSizingBoxLayout(orientation=self.orientation, anchor=self.anchor)
        self.container.bind(size=self.do_size)
        Widget.add_widget(self, self.container, *args, **kwargs)

    def add_widget(self, widget, *args, **kwargs):
        if self.container is None:
            self.make_container(*args, **kwargs)

        self.container.add_widget(widget, *args, **kwargs)

    def clear_widgets(self, *args, **kwargs):
        if self.container is None:
            self.make_container(*args, **kwargs)
        self.container.clear_widgets(*args, **kwargs)

    def do_size(self, *args):
        self.width = self.container.width * mm(1)
        self.height = self.container.height * mm(1)


    def n_children(self):  # number of children
        return len(self.container.children) if self.container is not None else 0
