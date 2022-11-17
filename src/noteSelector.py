from kivy.graphics import PopMatrix, PushMatrix, Scale, Translate, Color
from kivy.uix.relativelayout import RelativeLayout

from config.config import Config
from symbol import Symbol


class NoteSelector(RelativeLayout):
    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.update_note_pain()

    def update_note_pain(self):
        self.clear_widgets()

        currentNotePainInfo = Config.notePains[Config.currentNotePain]
        for noteInfo in currentNotePainInfo:
            with self.canvas:
                PushMatrix()
                Translate(*noteInfo.pos, 0)

                Color(*noteInfo.color)

            self.add_widget(Symbol(noteInfo.symbol, noteInfo.size))

            with self.canvas:
                PopMatrix()
