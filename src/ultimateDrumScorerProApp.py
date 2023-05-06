import os

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

from assembler import Assembler
from editor import Editor
from score import ScoreSectionStorage, ScoreSectionSectionStorage, TextStorage, ScoreStorageItem
from score.scoreFileHandling import saveScoreToFile, readScoreFromFile


class UltimateDrumScorerProApp(App):
    score: list[ScoreStorageItem]
    score_path: str

    def __init__(self, score_path="./testing.udsp"):
        App.__init__(self)
        self.score_path = score_path  # TODO: Make this not a horrible system

    def build(self):
        boxLayout = BoxLayout(orientation="vertical")
        editor = Editor()

        if self.score_path is None and not os.path.exists(self.score_path) and True:
            self.score = [
                TextStorage(pos=(0, 0), text="*hi* **how** __are__ _you_ ~~today~~"),
                ScoreSectionStorage([
                    ScoreSectionSectionStorage(note_ids=[0, 1]),
                    ScoreSectionSectionStorage(note_ids=[0])
                ], pos=(210 / 2, 297 / 2), normal_editor_note_ids=[0, 1, 6, 8])
            ]
        else:
            self.score = readScoreFromFile(self.score_path)

        boxLayout.add_widget(Assembler(editor, [self.score]))
        boxLayout.add_widget(editor)
        Window.bind(size=lambda _, size: self.update_size(boxLayout, size))

        return boxLayout

    def update_size(self, widget, size):
        widget.size = size

    def on_stop(self):
        saveScoreToFile(self.score_path, self.score)
