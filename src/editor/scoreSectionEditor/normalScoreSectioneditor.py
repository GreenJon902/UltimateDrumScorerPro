from kivy import Logger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import mm
from kivy.properties import ObjectProperty, OptionProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.widget import Widget

from assembler.pageContent.scoreSection import ScoreSection
from score import fix_and_get_normal_editor_note_ids, ScoreSectionStorage
from score.notes import notes
from selfSizingBoxLayout import SelfSizingBoxLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor.kv")


# noinspection PyPep8Naming
class NormalScoreSectionEditor_NoteEditor(RelativeLayout):
    bottom_note_y_offset: int = NumericProperty()


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


class EditorHolder(ZoomedLayout):
    bottom_note_y_offset: int = NumericProperty()

    def set_editor(self, editor: NormalScoreSectionEditor_NoteEditor):
        self.add_widget(editor)
        editor.bind(bottom_note_y_offset=lambda _, value: setattr(self, "bottom_note_y_offset", value))
        self.bottom_note_y_offset = editor.bottom_note_y_offset



class NormalScoreSectionEditor(TabbedPanelItem):
    score_section_instance: ScoreSection

    label_holder: SelfSizingBoxLayout = ObjectProperty()
    editor_holder: EditorHolder = ObjectProperty()
    editor: NormalScoreSectionEditor_NoteEditor = ObjectProperty()

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        self.trigger_update_labels = Clock.create_trigger(self._update_labels, -1)

        TabbedPanelItem.__init__(self, **kwargs)

        self.score_section_instance.score.bind(normal_editor_note_ids=self.trigger_update_labels)
        self.score_section_instance.score.bind_all(self.trigger_update_labels)
        self.trigger_update_labels()

        Clock.schedule_once(self.do_editor, -1)


    def do_editor(self, *args):
        if self.editor is not None:
            self.editor_holder.set_editor(self.editor)
        else:
            Logger.warning("NormalScoreSectionEditor: No editor supplied")

    def _update_labels(self, *args):
        note_ids = fix_and_get_normal_editor_note_ids(self.score_section_instance.score)
        ordered_note_types = sorted([notes[note_id] for note_id in note_ids], key=lambda x: x().note_level,
                                    reverse=True)  # Reverse cause of how they get added

        self.label_holder.clear_widgets()
        for note_type in ordered_note_types:
            note = note_type()
            self.label_holder.add_widget(NoteNameLabel(text=str(note.name), height=note.height *
                                                                                   self.editor_holder.scale))


class NoteNameLabel(Label):
    pass


class NoteSelector(BoxLayout):
    editor: NormalScoreSectionEditor = ObjectProperty()

    def __init__(self, **kwargs):
        self.do_height = Clock.create_trigger(self._do_height, -1)

        BoxLayout.__init__(self, **kwargs)
        self.do_height()

    def on_editor(self, _, value):
        for note_id in notes.keys():
            selector = NoteSelectorInside(note_id, value.score_section_instance.score)
            selector.bind(height=self.do_height)
            self.add_widget(selector)

    def _do_height(self, _):
        self.height = sum(child.height for child in self.children)


class NoteSelectorInside(RelativeLayout):  # Class that goes inside
    note_id: int = NumericProperty()
    score_section: ScoreSectionStorage = ObjectProperty()

    def __init__(self, note_id, score_section, **kwargs):
        self.note_id = note_id
        self.score_section = score_section
        self.note_obj = notes[note_id]()

        RelativeLayout.__init__(self, **kwargs)
