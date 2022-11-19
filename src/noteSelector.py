import math
from typing import Union

from kivy.core.window import Window
from kivy.graphics import PopMatrix, PushMatrix, Scale, Translate, Color
from kivy.properties import ListProperty
from kivy.uix.relativelayout import RelativeLayout

from config.config import Config
from symbol import Symbol


class NoteSelector(RelativeLayout):
    committed_notes: list[int] = ListProperty()
    current_hover: Union[int, None] = None

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)

        self.update_note_pain()

    def update_note_pain(self):
        self.clear_widgets()

        currentNotePainInfo = Config.notePains[Config.currentNotePain]
        for n, noteInfo in enumerate(currentNotePainInfo):

            symbol = Symbol(noteInfo.symbol, noteInfo.size)

            with self.canvas:
                PushMatrix()
                symbol.pos = noteInfo.pos

                color = Color(rgba=(Config.note_color if n in self.committed_notes else
                              Config.note_selector_uncommitted_color))
                symbol.color = color
            self.add_widget(symbol)
            Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

            with self.canvas:
                PopMatrix()

    def get_closest_to_pos(self, pos):
        """
        Get the closest symbol to the coordinates provided.

        :return: The symbol widget object, the distance away from the coords, the note id (the index)
        """

        distances = list()

        for symbol in self.children:
            absolute_center = symbol.get_absolute_center()
            dx = pos[0] - absolute_center[0]
            dy = pos[1] - absolute_center[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)

            distances.append(distance)

        distance = min(distances)
        index = distances.index(distance)
        symbol = self.children[index]

        return symbol, distance, index

    def mouse_move(self, pos):
        symbol, distance, index = self.get_closest_to_pos(pos)

        if distance <= Config.note_selector_distance:
            if self.current_hover != index and self.current_hover is not None:
                self.children[self.current_hover].color.rgba = Config.note_color \
                    if (self.current_hover in self.committed_notes) else \
                    Config.note_selector_uncommitted_color

            symbol.color.rgba = Config.note_selector_committed_hover_color \
                if (self.current_hover in self.committed_notes) else \
                Config.note_selector_uncommitted_hover_color
            self.current_hover = index

        elif distance > Config.note_selector_distance:
            symbol.color.rgba = symbol.color.rgba  # For some reason it breaks without this
            if self.current_hover is not None:
                symbol.color.rgba = Config.note_color if (index in self.committed_notes) else \
                    Config.note_selector_uncommitted_color
            self.current_hover = None

    def on_touch_up(self, touch):
        symbol, distance, index = self.get_closest_to_pos((touch.x, touch.y))
        if distance <= Config.note_selector_distance:
            if index in self.committed_notes:
                self.committed_notes.remove(index)
                symbol.color.rgba = Config.note_selector_uncommitted_hover_color
            else:
                self.committed_notes.append(index)
                symbol.color.rgba = Config.note_selector_committed_hover_color
