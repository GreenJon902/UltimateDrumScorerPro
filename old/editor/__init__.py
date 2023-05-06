from assembler.pageContent.scoreSection import ScoreSection
from assembler.pageContent.text import Text
from editor.scoreSectionEditor import ScoreSectionEditor
from editor.textEditor import TextEditor
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Builder.load_file("editor/editor.kv")


class Editor(RelativeLayout):
    opened_height: int
    selected: any

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        self.select(None)

    def select(self, obj):
        print(f"Selecting {obj}")
        self.clear_widgets()

        self.selected = obj
        if obj is None:
            self.opened_height = self.size_hint_y
            self.size_hint_y = 0  # Unselected so hide
            self.height = 0
        else:
            self.size_hint_y = self.opened_height

            if type(obj) == Text:
                self.add_widget(TextEditor(obj))
            elif type(obj) == ScoreSection:
                self.add_widget(ScoreSectionEditor(obj))
            else:
                raise TypeError(f"Expected object to be None / ScoreSection / Text, not {type(obj)}")

    def has_selected(self, obj):
        return self.selected == obj
