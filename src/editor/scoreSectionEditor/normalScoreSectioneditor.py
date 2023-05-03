from typing import Optional

from kivy import Logger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import mm
from kivy.properties import ObjectProperty, OptionProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.widget import Widget

from assembler.pageContent.scoreSection import ScoreSection
from score import fix_and_get_normal_editor_note_ids, ScoreSectionStorage
from score.decorations import decorations, Decoration
from score.notes import notes, Note
from selfSizingBoxLayout import SelfSizingBoxLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor.kv")


# noinspection PyPep8Naming
class NormalScoreSectionEditor_NoteEditor(RelativeLayout):
    bottom_note_y_offset: int = NumericProperty()
    current_decoration_editing_index: Optional[int] = NumericProperty(allownone=True, defaultvalue=None)

    score_section_instance: ScoreSection

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        kwargs.setdefault("current_decoration_editing_index", None)  # For some reason this is necessary
        RelativeLayout.__init__(self, **kwargs)


class AuxiliarySelector(RelativeLayout):
    def do_layout(self, *args):
        self.height = self.children[0].height if len(self.children) > 0 else 0
        RelativeLayout.do_layout(self, *args)


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
    auxiliary_selector: AuxiliarySelector = ObjectProperty()
    editing_spacing: bool = BooleanProperty(defaultvalue=False)
    editing_spacing_state: str = OptionProperty("what", options=["what", "equal_spacing_size", "dynamic_spacing_size"])
    # What is choosing how to edit spacing, equal_spacing means everything is the same, dynamic_spacing means
    # based off the rhythm

    note_selector: "NoteSelector"
    decoration_selector: "DecorationSelector"
    editing_spacing_method_selector: "EditingSpacingMethodSelector"
    equal_spacing_size_selector: "SpacingSliderAndExitButtons"

    update_auxiliary_selector_contents = None

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        self.note_selector = NoteSelector()
        self.decoration_selector = DecorationSelector()
        self.editing_spacing_method_selector = EditingSpacingMethodSelector()
        self.equal_spacing_size_selector = SpacingSliderAndExitButtons(
            change_callback=lambda _, x: self.set_spacings("equal", x), max=10)
        self.trigger_update_labels = Clock.create_trigger(self._update_labels, -1)
        self.update_auxiliary_selector_contents = Clock.create_trigger(self._update_auxiliary_selector_contents, -1)

        TabbedPanelItem.__init__(self, **kwargs)

        self.score_section_instance.storage.bind(normal_editor_note_ids=self.trigger_update_labels)
        self.score_section_instance.storage.bind_all(self.trigger_update_labels)
        self.trigger_update_labels()

        Clock.schedule_once(self.late_setup, -1)


    def set_spacings(self, type_, value):
        if type_ == "equal":
            for section in self.score_section_instance.storage:
                section.custom_width = value
        else:
            raise NotImplementedError()

    def late_setup(self, *args):  # Set up stuff once all the properties are filled
        if self.editor is not None:
            self.editor_holder.set_editor(self.editor)
        else:
            Logger.warning("NormalScoreSectionEditor: No editor supplied")
        self.note_selector.editor = self.editor
        self.decoration_selector.editor = self.editor
        self.editing_spacing_method_selector.normal_editor = self
        self.equal_spacing_size_selector.normal_editor = self
        self.auxiliary_selector.add_widget(self.note_selector)

        self.editor.bind(current_decoration_editing_index=self.update_auxiliary_selector_contents)
        self.bind(editing_spacing_state=self.update_auxiliary_selector_contents)

    def on_editing_spacing(self, _, value):
        if value:
            self.editing_spacing_state = "what"  # Reset this value
        self.update_auxiliary_selector_contents()

    def _update_auxiliary_selector_contents(self, _):
        self.auxiliary_selector.clear_widgets()

        if self.editing_spacing:
            if self.editing_spacing_state == "what":
                self.editing_spacing_method_selector.height = self.auxiliary_selector.parent.height
                self.auxiliary_selector.add_widget(self.editing_spacing_method_selector)
            elif self.editing_spacing_state == "equal_spacing_size":
                self.equal_spacing_size_selector.height = self.auxiliary_selector.parent.height
                self.auxiliary_selector.add_widget(self.equal_spacing_size_selector)
            elif self.editing_spacing_state == "dynamic_spacing_size":
                raise NotImplementedError()
        else:
            if self.editor.current_decoration_editing_index is None:
                self.auxiliary_selector.add_widget(self.note_selector)
            else:
                self.auxiliary_selector.add_widget(self.decoration_selector)

    def _update_labels(self, *args):
        note_ids = fix_and_get_normal_editor_note_ids(self.score_section_instance.storage)
        ordered_note_types = sorted([notes[note_id] for note_id in note_ids], key=lambda x: x().note_level,
                                    reverse=True)  # Reverse cause of how they get added

        self.label_holder.clear_widgets()
        for note_type in ordered_note_types:
            note = note_type()
            self.label_holder.add_widget(NoteNameLabel(text=str(note.name), height=note.height *
                                                                                   self.editor_holder.scale))



class NoteNameLabel(Label):
    pass


class Selector(BoxLayout):
    editor: NormalScoreSectionEditor_NoteEditor = ObjectProperty()

    def __init__(self, **kwargs):
        self.do_height = Clock.create_trigger(self._do_height, -1)

        BoxLayout.__init__(self, **kwargs)
        self.do_height()


    def _do_height(self, _):
        self.height = sum(child.height for child in self.children)


class NoteSelector(Selector):
    def on_editor(self, _, value):
        for note_id in notes.keys():
            selector = NoteSelectorInside(note_id, value.score_section_instance.storage)
            selector.bind(size=self.do_height)
            self.add_widget(selector)
        self.do_height()


class NoteSelectorInside(RelativeLayout):  # Class that goes inside note selector
    note_id: int
    score_section: ScoreSectionStorage
    note_obj: Note

    def __init__(self, note_id, score_section, **kwargs):
        self.note_id = note_id
        self.score_section = score_section
        self.note_obj = notes[note_id]()

        RelativeLayout.__init__(self, **kwargs)


class DecorationSelector(Selector):
    insides: dict[int, "DecorationSelectorInside"]

    def __init__(self, **kwargs):
        self.insides = {}

        Selector.__init__(self, **kwargs)
        for decoration_id in decorations.keys():
            selector = DecorationSelectorInside(decoration_id, self.on_click)
            selector.bind(size=self.do_height)
            self.add_widget(selector)
            self.insides[decoration_id] = selector

    def on_parent(self, _, __):
        index = self.editor.current_decoration_editing_index
        if index is not None:
            did = self.editor.score_section_instance.storage[index].decoration_id
            if did is None:
                for inside in self.insides.values():
                    inside.checkbox.active = False
            else:
                self.insides[did].checkbox.active = True

    def on_click(self, decoration_id, state):
        #  If state is true then we set it regardless, if it is false and the ids are equal then set it to none
        if state:
            self.editor.score_section_instance.storage[self.editor.current_decoration_editing_index].decoration_id = \
                decoration_id
        elif decoration_id == self.editor.score_section_instance.storage[self.editor.current_decoration_editing_index]\
                .decoration_id:
            self.editor.score_section_instance.storage[self.editor.current_decoration_editing_index].decoration_id = None


class DecorationSelectorInside(RelativeLayout):
    decoration_id: int
    decoration_obj: Decoration
    click_callback: callable
    container: RelativeLayout = ObjectProperty()
    checkbox: CheckBox = ObjectProperty()

    def __init__(self, decoration_id, click_callback, **kwargs):
        self.decoration_id = decoration_id
        self.decoration_obj = decorations[decoration_id](color=(1, 1, 1, 1))
        self.click_callback = click_callback

        RelativeLayout.__init__(self, **kwargs)

    def on_container(self, _, value):
        value.add_widget(self.decoration_obj)


class EditingSpacingMethodSelector(RelativeLayout):
    normal_editor: NormalScoreSectionEditor = ObjectProperty()


class SpacingSliderAndExitButtons(RelativeLayout):
    change_callback: callable = ObjectProperty()
    min: int = NumericProperty()
    max: int = NumericProperty()
    normal_editor: NormalScoreSectionEditor = ObjectProperty()
