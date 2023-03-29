import re

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.textinput import TextInput

from assembler.pageContent.scoreSection import ScoreSection
from score import ScoreSectionStorage, ScoreSectionSectionStorage
from score.notes import notes

Builder.load_file("editor/scoreSectionEditor/textScoreSectionEditor.kv")


class TextScoreSectionEditor(TabbedPanelItem):
    score_section_instance: ScoreSection
    _old_score_section_storage: ScoreSectionStorage = None

    trigger_set_content = None
    parser_regex = re.compile(r"(-?\d+) +(\d+) +(\d+(,\d+)*) *\n+")

    text_input: TextInput = ObjectProperty(allownone=True)
    _old_text_input = None


    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        self.trigger_set_content = Clock.create_trigger(self._set_content, -1)

        TabbedPanelItem.__init__(self, **kwargs)
        self.score_section_instance.bind(score=self.on_score_section_instance_score)
        self.trigger_set_content()

    def on_text_input(self, _, value):
        if self._old_text_input is not None:
            self._old_text_input.unbind(text=self.on_text_input_text)
        value.bind(text=self.on_text_input_text)

    def on_score_section_instance_score(self, _, value):
        if self._old_score_section_storage is not None:
            self._old_score_section_storage.unbind_all(self.trigger_set_content)
        value.bind_all(self.trigger_set_content)

    def _set_content(self, *args):  # Set content to what's in score_section_instance.score
        string = ""
        section: ScoreSectionSectionStorage
        for section in self.score_section_instance.score.sections:
            string += str(section.delta_bars) + " "
            string += str(section.dots) + " "
            string += ",".join(str(n_id) for n_id in section.note_ids) + "\n"
        self.text_input.text = string

    def on_text_input_text(self, _, value):
        sections: list[ScoreSectionSectionStorage] = []
        for group in self.parser_regex.findall(value):
            delta_bars = int(group[0])
            dots = int(group[1])
            note_ids = {(int(n_id) if n_id != "" else "") for n_id in group[2].split(",")}
            for n_id in note_ids.copy():
                if n_id not in notes:
                    note_ids.remove(n_id)  # Also gets ""
                    print(f"User tried inputting an unknown note id - {n_id}")
            sections.append(ScoreSectionSectionStorage(delta_bars=delta_bars, dots=dots, note_ids=note_ids))
        self.score_section_instance.score.sections = sections
