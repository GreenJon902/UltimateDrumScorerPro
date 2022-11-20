import math
from typing import Union

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ListProperty, BooleanProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout

from config.config import Config
from symbol import Symbol


class Section(RelativeLayout):
    committed_notes: list[int] = ListProperty()
    current_hover: Union[int, None] = None

    symbols: dict[int, Symbol]
    focused: bool = BooleanProperty(defaultvalue=False)
    forced_width: int = NumericProperty(allownone=True, defaultvalue=None)  # For when section is used as a spacer

    def __init__(self, **kwargs):
        self.symbols = {}
        self.calculate_size = Clock.create_trigger(lambda _: self._calculate_size())
        self.bind(forced_width=lambda _, __: self.calculate_size())

        RelativeLayout.__init__(self, **kwargs)

        self.size_hint_x = None
        self.size_hint_y = None

        highest = max(Config.note_info, key=lambda x: x.y + x.height)
        self.height = highest.y + highest.height

        self.redraw()

    def redraw(self):
        self.clear_widgets()
        self.canvas.clear()
        taken_y_levels: dict[float, float] = {}

        for n, noteInfo in enumerate(Config.note_info):
            symbol = Symbol(noteInfo.symbol, noteInfo.size)
            symbol.y = noteInfo.y + Config.section_bottom_buffer

            if symbol.y in taken_y_levels.keys():
                symbol.expanded_x = taken_y_levels[symbol.y] + Config.section_x_buffer
                taken_y_levels[symbol.y] += noteInfo.width + Config.note_selector_x_space
            else:
                symbol.expanded_x = Config.section_x_buffer
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

        if self.forced_width is None:
            self.width = max(widths.values()) + Config.section_x_buffer * 2
        else:
            self.width = self.forced_width
        self.height = max(self.symbols.values(), key=lambda x: x.y + x.height).top + \
            Config.section_bottom_buffer + Config.section_top_buffer


    def kill_self(self, animated=False):
        """
        Remove this section from parent without it looking like poo.
        :return:
        """
        if animated:
            for index in self.symbols.keys():
                symbol = self.symbols[index]

                a = (Animation(x=Config.section_x_buffer, y=symbol.y + Config.section_kill_rise_amount, transparency=0,
                               duration=Config.section_kill_speed))
                a.start(symbol)

            self.forced_width = self.width
            a = Animation(forced_width=0, duration=Config.section_kill_speed)
            a.start(self)

            Clock.schedule_once(lambda _: self.parent.remove_widget(self), Config.section_kill_speed)


    def on_focused(self, _, focused, animation_duration=Config.focus_speed):
        if not focused and len(self.committed_notes) == 0:  # Empty so delete
            self.kill_self(animated=True)
            return

        taken_lines: list[float] = []  # Whether a line already has something on it and then other piece needs to be
                                       # on the other side. Only used when not focused

        for index in self.symbols.keys():
            symbol = self.symbols[index]

            if focused:
                a = Animation(x=symbol.expanded_x, transparency=(1 if index in self.committed_notes else
                                                                 Config.note_selector_uncommitted_transparency),
                              duration=animation_duration)
                a.start(symbol)

            else:
                x = Config.section_x_buffer
                if self.symbols[index].y in taken_lines and index in self.committed_notes:
                    x += self.symbols[index].width

                a = Animation(x=x, transparency=(1 if index in self.committed_notes else 0),
                              duration=animation_duration)
                a.start(symbol)
                a = Animation(r=0, g=0, b=0,
                              duration=animation_duration)
                a.start(symbol.color)

                if index in self.committed_notes:
                    taken_lines.append(self.symbols[index].y)


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
                    amount = 0  # There can only be 2 per line
                    for i in self.committed_notes:
                        if self.symbols[i].y == symbol.y:
                            amount += 1
                    if amount < 2:

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
