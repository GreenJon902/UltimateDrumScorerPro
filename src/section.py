import math
from typing import Union

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ListProperty, BooleanProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout

from config.config import Config
from newSectionButton import NewSectionButton
from sectionExtender import SectionExtender
from symbol import Symbol
from trashCanButton import TrashCanButton


class Section(RelativeLayout):
    committed_notes: list[int] = ListProperty()
    current_hover: Union[int, None] = None

    symbols: dict[int, Symbol]
    focused: bool = BooleanProperty(defaultvalue=False)
    forced_width: Union[int, None] = NumericProperty(allownone=True, defaultvalue=None)  # For when section is used as a
                                                                                         # spacer
    new_section_button_x_space_multiplier: int = NumericProperty()  # For focusing and un-focusing
    parent_x_buffer_multiplier: int = NumericProperty()  # For the parents x buffer space
    stem_x: int = NumericProperty()  # For the parents drawing of stems

    section_extender_enabled = BooleanProperty(defaultvalue=False)
    section_extender_hovered = BooleanProperty(defaultvalue=False)
    section_extender_acting = BooleanProperty(defaultvalue=False)

    trash_can_button: TrashCanButton = None
    section_extender: SectionExtender = None
    new_section_button: NewSectionButton = None
    being_killed: bool = False

    def __init__(self, entrance_animated=False, **kwargs):
        self.symbols = {}
        self.calculate_size = Clock.create_trigger(lambda _: self._calculate_size(), -1)
        self.bind(forced_width=lambda _, __: self.calculate_size(),
                  new_section_button_x_space_multiplier=lambda _, __: self.calculate_size())
        Window.bind(mouse_pos=lambda _, pos: self.mouse_move(pos))

        RelativeLayout.__init__(self, **kwargs)

        self.size_hint_x = None
        self.size_hint_y = None

        highest = max(Config.note_info, key=lambda x: x.y + x.height)
        self.height = highest.y + highest.height

        self.redraw(entrance_animated)

    def redraw(self, entrance_animated):
        self.clear_widgets()
        self.canvas.clear()
        taken_y_levels: dict[float, float] = {}

        for n, noteInfo in enumerate(Config.note_info):
            symbol = Symbol(noteInfo.symbol, noteInfo.size)
            if entrance_animated:
                symbol.right = 0
            symbol.y = noteInfo.y + Config.section_extender_space

            if symbol.y in taken_y_levels.keys():
                symbol.expanded_x = taken_y_levels[symbol.y]
                taken_y_levels[symbol.y] += noteInfo.width + Config.note_selector_x_space
            else:
                symbol.expanded_x = 0
                taken_y_levels[symbol.y] = noteInfo.width + Config.note_selector_x_space

            symbol.bind(pos=lambda _, __: self.calculate_size(), size=lambda _, __: self.calculate_size())

            self.add_widget(symbol)
            self.symbols[n] = symbol


        self.trash_can_button = TrashCanButton(Config.section_trash_can_size)
        self.trash_can_button.bind(y=lambda _, __: self.calculate_size())
        self.trash_can_button.y = 0  # x is managed in self._calculate_size
        self.add_widget(self.trash_can_button)

        self.section_extender = SectionExtender(Config.section_extender_height)  # width managed in self._calculate_size
        self.section_extender.bind(pos=lambda _, __: self.calculate_size(), height=lambda _, __: self.calculate_size())
        self.section_extender.x = 0
        self.section_extender.y = 0
        self.add_widget(self.section_extender)

        self.new_section_button = NewSectionButton(Config.new_section_button_size)
        self.new_section_button.y = self.height / 2 - self.new_section_button.height / 2
            # x is managed in self._calculate_size
        self.add_widget(self.new_section_button)

        if entrance_animated:
            a = Animation(parent_x_buffer_multiplier=1, duration=Config.section_entrance_animation_duration)
            a.start(self)

            self.on_focused(self, self.focused, animation_duration=Config.section_entrance_animation_duration)
        else:
            self.parent_x_buffer_multiplier = 1
            self.on_focused(self, self.focused, animation_duration=0)
        self.calculate_size()

    def _calculate_size(self):
        widths: dict[int, float] = {}

        for index in self.symbols.keys():
            symbol = self.symbols[index]

            widths[index] = symbol.x + symbol.width

        if self.forced_width is None:
            self.width = max(widths.values()) + (Config.new_section_button_x_buffer + self.new_section_button.width) * self.new_section_button_x_space_multiplier
        else:
            self.width = self.forced_width

        self.height = max(self.symbols.values(), key=lambda x: x.y + x.height).top


        self.new_section_button.right = self.width

        if not self.being_killed:
            self.trash_can_button.right = self.new_section_button.x - Config.new_section_button_x_buffer * \
                                          self.new_section_button_x_space_multiplier

            self.section_extender.width = self.trash_can_button.x - \
                                          Config.section_extender_trash_can_buffer

            if self.section_extender.width < 0:  # This would mainly be caused the Config.new_section_button_x_buffer
                self.section_extender.width = 0
                self.trash_can_button.x = self.section_extender.width + Config.section_extender_trash_can_buffer




    def kill_self(self, animated=False):
        """
        Remove this section from parent without it looking like poo.
        :return:
        """
        if not self.being_killed:
            self.being_killed = True

            if animated:
                for index in self.symbols.keys():
                    symbol = self.symbols[index]

                    a = (Animation(x=0, y=symbol.y + Config.section_kill_rise_amount,
                                   transparency=0,
                                   duration=Config.section_kill_speed))
                    a.start(symbol)

                a = (Animation(transparency=0,
                               duration=Config.section_kill_speed))
                a.start(self.trash_can_button)

                a = (Animation(width=0, transparency=0,
                               duration=Config.section_kill_speed))
                a.start(self.section_extender)

                a = Animation(transparency=0,
                              duration=Config.section_kill_speed)
                a.start(self.new_section_button)
                a = Animation(new_section_button_x_space_multiplier=0,
                              duration=Config.section_kill_speed)
                a.start(self)


                self.forced_width = self.width
                a = Animation(forced_width=0, parent_x_buffer_multiplier=0, duration=Config.section_kill_speed)
                a.start(self)

                Clock.schedule_once(lambda _: self.parent.remove_widget(self), Config.section_kill_speed)
            else:
                self.parent.remove_widget(self)


    def on_focused(self, _, focused, animation_duration=Config.focus_speed, unset_forced_width_at_end=False):
        if not focused and len(self.committed_notes) == 0 and not self.section_extender_enabled:  # Empty so delete
            self.kill_self(animated=True)
            return

        if not self.being_killed:
            taken_lines: list[float] = []  # Whether a line already has something on it and then other piece needs to be
                                           # on the other side. Only used when not focused
            max_symbol_width: float = max([(self.symbols[index].width if index in self.committed_notes else 0)
                                           for index in self.symbols.keys()])  # For correct aligning to note stem.
                                                                               # Only used when not focused

            for index in self.symbols.keys():
                symbol = self.symbols[index]

                if focused and not self.section_extender_enabled:
                    a = Animation(x=symbol.expanded_x, transparency=(1 if index in self.committed_notes else
                                                                     Config.note_selector_uncommitted_transparency),
                                  duration=animation_duration)
                    a.start(symbol)

                else:
                    x = 0
                    if index in self.committed_notes:
                        if self.symbols[index].y in taken_lines:
                            x += self.symbols[index].width

                        elif symbol.width < max_symbol_width:  # first note needs to be aligned correctly
                            x = max_symbol_width - symbol.width

                    a = Animation(x=x, transparency=(1 if index in self.committed_notes else 0),
                                  duration=animation_duration)
                    a.start(symbol)
                    a = Animation(r=0, g=0, b=0,  # Make sure everything is black
                                  duration=animation_duration)
                    a.start(symbol.color)

                    if index in self.committed_notes:
                        taken_lines.append(self.symbols[index].y)


            a = Animation(transparency=(Config.section_trash_can_transparency if focused else 0),
                          duration=animation_duration)  # x is managed in self._calculate_size
            a.start(self.trash_can_button)

            a = Animation(transparency=(((1 if self.section_extender_enabled else Config.section_extender_transparency)
                                         if focused else 0)),
                          duration=animation_duration)  # x is as far left as it will get
            a.start(self.section_extender)

            a = Animation(transparency=(Config.new_section_button_transparency if focused else 0),
                          duration=animation_duration)
            a.start(self.new_section_button)
            a = Animation(new_section_button_x_space_multiplier=(1 if focused else 0),
                          duration=animation_duration)
            a.start(self)

            if unset_forced_width_at_end:
                Clock.schedule_once(lambda _: self.unset_forced_width(), animation_duration)


    def unset_forced_width(self):
        Clock.schedule_once(lambda _: self._unset_forced_width(), 0)  # Wait a frame

    def _unset_forced_width(self):
        self.forced_width = None  # TODO: Animate this returning to normal focused width


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
        if self.focused and not self.being_killed and not self.section_extender_enabled:
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


            if self.trash_can_button.collide_point(*self.to_local(*pos)):
                a = Animation(transparency=1,
                              duration=Config.section_trash_can_hover_fade_speed)
                a.start(self.trash_can_button)
            elif self.trash_can_button.transparency == 1:  # Was hovered but isn't anymore
                a = Animation(transparency=Config.section_trash_can_transparency,
                              duration=Config.section_trash_can_hover_fade_speed)
                a.start(self.trash_can_button)

            if self.section_extender.collide_point(*self.to_local(*pos)):
                a = Animation(transparency=Config.section_extender_hover_transparency,
                              duration=Config.section_extender_hover_fade_speed)
                a.start(self.section_extender)
            elif self.section_extender.transparency == Config.section_extender_hover_transparency:  # Was hovered but
                                                                                                    # isn't anymore
                a = Animation(transparency=(1 if self.section_extender_enabled else
                                            Config.section_extender_transparency),
                              duration=Config.section_extender_hover_fade_speed)
                a.start(self.section_extender)

            if self.new_section_button.collide_point(*self.to_local(*pos)):
                a = Animation(transparency=1,
                              duration=Config.new_section_button_hover_fade_speed)
                a.start(self.new_section_button)
            elif self.new_section_button.transparency == 1:  # Was hovered but isn't anymore

                a = Animation(transparency=Config.new_section_button_transparency,
                              duration=Config.new_section_button_hover_fade_speed)
                a.start(self.new_section_button)

        if self.section_extender.over_arrow(*self.to_local(*pos)) and self.section_extender_enabled:
            Window.set_system_cursor("size_we")
            self.section_extender_hovered = True
        elif self.section_extender_hovered:
            Window.set_system_cursor("arrow")
            self.section_extender_hovered = False


    def on_touch_down(self, touch):
        if self.section_extender_enabled and self.section_extender.over_arrow(*self.to_widget(*touch.pos)):
            self.section_extender_acting = True

    def on_touch_move(self, touch):
        if self.section_extender_acting:
            self.forced_width += touch.dx

        else:
            return RelativeLayout.on_touch_move(self, touch)

    def on_touch_up(self, touch):
        if self.section_extender_acting:
            self.section_extender_acting = False

        elif self.focused and not self.being_killed:
            if not self.section_extender_enabled:
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


            if self.trash_can_button.collide_point(*self.to_widget(*touch.pos)):
                self.kill_self(animated=True)


            if self.section_extender.collide_point(*self.to_widget(*touch.pos)):
                self.section_extender_enabled = not self.section_extender_enabled


            if self.new_section_button.collide_point(*self.to_widget(*touch.pos)):
                self.parent.add_new(self)


    def on_section_extender_enabled(self, _, enabled):
        if not self.being_killed:
            if enabled:
                self.forced_width = self.width
            else:
                self.on_focused(self, self.focused, unset_forced_width_at_end=True)

            self.on_focused(self, self.focused)

            a = Animation(transparency=(1 if enabled else Config.section_extender_hover_transparency),
                          duration=Config.section_extender_hover_fade_speed)
            a.start(self.section_extender)
