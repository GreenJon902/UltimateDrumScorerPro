import math
from typing import Union

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import PopMatrix, PushMatrix, Scale, Translate, Color
from kivy.properties import ListProperty, BooleanProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout

from config.config import Config
from symbol import Symbol


class Notes(RelativeLayout):
    committed_notes: list[int] = ListProperty()
    current_hover: Union[int, None] = None

    symbols: dict[int, Symbol]
    focused: bool = BooleanProperty(defaultvalue=False)

    def __init__(self, **kwargs):
        self.symbols = {}
        self.calculate_size = Clock.create_trigger(lambda _: self._calculate_size())

        RelativeLayout.__init__(self, **kwargs)

        self.size_hint_x = None
        self.size_hint_y = None

        highest = max(Config.note_info, key=lambda x: x.y + x.height)
        self.height = highest.y + highest.height

        self.update()

    def update(self):
        self.clear_widgets()
        taken_y_levels: dict[float, float] = {}

        for n, noteInfo in enumerate(Config.note_info):
            symbol = Symbol(noteInfo.symbol, noteInfo.size)
            symbol.y = noteInfo.y

            if symbol.y in taken_y_levels.keys():
                symbol.expanded_x = taken_y_levels[symbol.y]
                taken_y_levels[symbol.y] += noteInfo.width + Config.note_selector_x_space
            else:
                symbol.expanded_x = 0
                taken_y_levels[symbol.y] = noteInfo.width + Config.note_selector_x_space

            symbol.bind(pos=lambda _, __: self.calculate_size(), size=lambda _, __: self.calculate_size())

            self.add_widget(symbol)
            self.symbols[n] = symbol

        Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

        self.on_focused(self, self.focused, animation_duration=0)
        self.calculate_size()

    def _calculate_size(self):
        widths: dict[int, float] = {}

        for index in self.symbols.keys():
            symbol = self.symbols[index]

            widths[index] = symbol.x + symbol.width

        self.width = max(widths.values())
        self.height = max(self.symbols.values(), key=lambda x: x.y + x.height).top

    def on_width(self, _, width):
        self.parent.translate.x = 0#-width

    def on_focused(self, _, focused, animation_duration=Config.focus_speed):
        for index in self.symbols.keys():
            symbol = self.symbols[index]

            if focused:
                a = Animation(x=symbol.expanded_x, transparency=(1 if index in self.committed_notes else
                                                                 Config.note_selector_uncommitted_transparency),
                              duration=animation_duration)
                a.start(symbol)
            else:
                a = Animation(x=0, transparency=(1 if index in self.committed_notes else 0),
                              duration=animation_duration)
                a.start(symbol)


    def get_closest_to_pos(self, pos):
        distances = {}

        for i in self.symbols.keys():
            absolute_center = self.symbols[i].get_absolute_center()
            dx = pos[0] - absolute_center[0]
            dy = pos[1] - absolute_center[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)

            distances[i] = distance

        index = min(distances.keys(), key=lambda x: distances[x])
        distance = distances[index]

        return index, distance


    def mouse_move(self, pos):
        if self.focused:
            index, distance = self.get_closest_to_pos(pos)
            symbol = self.symbols[index]

            if distance <= Config.note_selector_distance and self.current_hover != index:
                if self.current_hover is not None:
                    a = Animation(r=0, g=0, b=0,
                                  duration=Config.note_hover_color_fade_speed)
                    a.start(self.symbols[self.current_hover].color)

                a = Animation(r=(Config.note_selector_committed_hover_color[0] if index in self.committed_notes else
                                 Config.note_selector_uncommitted_hover_color[0]),
                              b=(Config.note_selector_committed_hover_color[1] if index in self.committed_notes else
                                 Config.note_selector_uncommitted_hover_color[1]),
                              g=(Config.note_selector_committed_hover_color[2] if index in self.committed_notes else
                                 Config.note_selector_uncommitted_hover_color[2]),
                              duration=Config.note_hover_color_fade_speed)
                a.start(symbol.color)
                self.current_hover = index

            elif distance > Config.note_selector_distance:
                if self.current_hover is not None:
                    a = Animation(r=0, g=0, b=0,
                                  duration=Config.note_hover_color_fade_speed)
                    a.start(symbol.color)
                self.current_hover = None


    def on_touch_up(self, touch):
        if self.focused:
            index, distance = self.get_closest_to_pos((touch.x, touch.y))
            symbol = self.symbols[index]

            if distance <= Config.note_selector_distance:
                if index in self.committed_notes:
                    self.committed_notes.remove(index)
                else:
                    self.committed_notes.append(index)

                a = Animation(transparency=(1 if index in self.committed_notes else
                                            Config.note_selector_uncommitted_transparency),
                              duration=Config.note_commit_speed)
                a.start(symbol)
                a = Animation(r=(Config.note_selector_committed_hover_color[0] if index in self.committed_notes else
                                 Config.note_selector_uncommitted_hover_color[0]),
                              b=(Config.note_selector_committed_hover_color[1] if index in self.committed_notes else
                                 Config.note_selector_uncommitted_hover_color[1]),
                              g=(Config.note_selector_committed_hover_color[2] if index in self.committed_notes else
                                 Config.note_selector_uncommitted_hover_color[2]),
                              duration=Config.note_hover_color_fade_speed)
                a.start(symbol.color)
