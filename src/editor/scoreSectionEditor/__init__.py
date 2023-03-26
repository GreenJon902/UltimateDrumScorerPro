from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

from assembler.pageContent.scoreSection import ScoreSection
from editor.scoreSectionEditor.textScoreSectionEditor import TextScoreSectionEditor

Builder.load_file("editor/scoreSectionEditor/scoreSectionEditor.kv")



class ScoreSectionEditor(TabbedPanel):
    enabled_tab_color = ColorProperty()
    disabled_tab_color = ColorProperty()

    score_section_instance: ScoreSection

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance

        TabbedPanel.__init__(self, **kwargs)
        Clock.schedule_once(self.on_tab_width, 1)  # As custom tab widths

        self.add_widget(TextScoreSectionEditor(score_section_instance))  # TODO: Load these from a settings system
        self.add_widget(TabbedPanelItem(text="Spacing"))