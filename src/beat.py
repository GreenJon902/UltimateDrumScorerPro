from kivy.core.window import Window
from kivy.graphics import Translate, PushMatrix, PopMatrix
from kivy.uix.boxlayout import BoxLayout

from config.config import Config
from section import Section


class Beat(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        with self.canvas.before:
            PushMatrix()
            self.translate = Translate()

        for i in range(Config.default_beat_section_count):
            self.add_widget(Section(committed_notes=[1]))

        with self.canvas.after:
            PopMatrix()

        Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

    def mouse_move(self, pos):
        for child in self.children:
            if child.collide_point(*pos):
                child.focused = True
            else:
                child.focused = False