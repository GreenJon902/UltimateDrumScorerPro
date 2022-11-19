
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout

from config.config import Config
from notes import Notes


class Section(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        self.spacing = Config.section_spacing

        for i in range(Config.default_section_beat_count):
            self.add_widget(Notes(committed_notes=[4, 7]))
