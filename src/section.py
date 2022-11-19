from kivy.core.window import Window
from kivy.graphics import Translate, PushMatrix, PopMatrix
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter

from config.config import Config
from notes import Notes


class Section(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        with self.canvas.before:
            PushMatrix()
            self.translate = Translate()

        for i in range(Config.default_section_beat_count):
            self.add_widget(Notes(committed_notes=[1]))

        with self.canvas.after:
            PopMatrix()

        Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

    def mouse_move(self, pos):
        for child in self.children:
            if child.collide_point(*pos):
                child.focused = True
            else:
                child.focused = False
