from editor.scoreSectionEditor.normalScoreSectioneditor import NormalScoreSectionEditor_Editor, AuxiliarySelector, \
    NormalScoreSectionEditor
from kivy.lang import Builder
from kivy.properties import OptionProperty, ObjectProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor_SpacingEditor.kv")


# noinspection PyPep8Naming
class NormalScoreSectionEditor_SpacingEditor(NormalScoreSectionEditor_Editor):
    editing_spacing_state: str = OptionProperty("what", options=["what", "equal_spacing_size", "dynamic_spacing_size"])
    # What is choosing how to edit spacing, equal_spacing means everything is the same, dynamic_spacing means
    # based off the rhythm
    
    def __init__(self, score_section_instance, **kwargs):
        NormalScoreSectionEditor_Editor.__init__(self, score_section_instance, **kwargs)
        self.canvas.add(score_section_instance.canvas)


    editing_spacing_method_selector: "EditingSpacingMethodSelector"
    equal_spacing_size_selector: "SpacingSliderAndExitButtons"
    auxiliary_selector: AuxiliarySelector

    def auxiliary_selector_setup(self, auxiliary_selector: AuxiliarySelector):
        self.auxiliary_selector = auxiliary_selector
        
        self.editing_spacing_method_selector = EditingSpacingMethodSelector()
        self.equal_spacing_size_selector = SpacingSliderAndExitButtons(
            change_callback=lambda _, x: self.set_spacings("equal", x), max=10)

        self.editing_spacing_method_selector.normal_editor = self
        self.equal_spacing_size_selector.normal_editor = self

        self.bind(editing_spacing_state=self.update_auxiliary_selector_contents)
        self.auxiliary_selector.parent.bind(height=self.update_auxiliary_selector_contents)

    def _update_auxiliary_selector_contents(self, _):
        self.auxiliary_selector.clear_widgets()

        if self.editing_spacing_state == "what":
            self.editing_spacing_method_selector.height = self.auxiliary_selector.parent.height
            self.auxiliary_selector.add_widget(self.editing_spacing_method_selector)
        elif self.editing_spacing_state == "equal_spacing_size":
            self.equal_spacing_size_selector.height = self.auxiliary_selector.parent.height
            self.auxiliary_selector.add_widget(self.equal_spacing_size_selector)
        elif self.editing_spacing_state == "dynamic_spacing_size":
            raise NotImplementedError()

    def set_spacings(self, type_, value):
        if type_ == "equal":
            for section in self.score_section_instance.storage:
                section.custom_width = value
        else:
            raise NotImplementedError()


class EditingSpacingMethodSelector(RelativeLayout):
    normal_editor: NormalScoreSectionEditor = ObjectProperty()


class SpacingSliderAndExitButtons(RelativeLayout):
    change_callback: callable = ObjectProperty()
    min: int = NumericProperty()
    max: int = NumericProperty()
    normal_editor: NormalScoreSectionEditor = ObjectProperty()
