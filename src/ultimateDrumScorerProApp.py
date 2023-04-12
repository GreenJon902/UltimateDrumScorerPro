from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

from assembler import Assembler
from assembler.pageContent.scoreSection import ScoreSection
from assembler.pageContent.text import Text
from editor import Editor
from score import ScoreSectionStorage, ScoreSectionSectionStorage


class UltimateDrumScorerProApp(App):
    def __init__(self):
        App.__init__(self)

    def build(self):
        boxLayout = BoxLayout(orientation="vertical")
        editor = Editor()
        boxLayout.add_widget(Assembler(
               [
                   [
                       Text(editor, pos=(0, 0), text="*hi* **how** __are__ _you_ ~~today~~"),
                       ScoreSection(editor, pos=(210 / 2, 297 / 2), score=ScoreSectionStorage([
                           ScoreSectionSectionStorage(note_ids=[0, 1]),
                           ScoreSectionSectionStorage(note_ids=[0])
                       ], normal_editor_note_ids=[0, 1, 6, 8])),
                   ]
               ]
            )
        )
        boxLayout.add_widget(editor)
        Window.bind(size=lambda _, size: self.update_size(boxLayout, size))

        return boxLayout

    def update_size(self, widget, size):
        widget.size = size
