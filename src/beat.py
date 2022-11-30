import math

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget

from bars import Bars
from config.config import Config
from section import Section
from stem import Stem


class Beat(Widget):
    killing: list[tuple[Section, Stem, Bars]]

    all_sections: list[Section]  # Includes items in self.killed
    all_barss: list[Bars]  # Includes items in self.killed
    sections: list[Section]
    stems: list[Stem]
    barss: list[Bars]

    def __init__(self, **kwargs):
        self.killing = list()

        self.all_sections = list()
        self.all_barss = list()
        self.sections = list()
        self.stems = list()
        self.barss = list()

        self.trigger_layout = Clock.create_trigger(self.do_layout, -1)
        self.trigger_focus_check = Clock.create_trigger(self.check_focus, -1)

        Window.bind(mouse_pos=self.trigger_focus_check)
        fbind = self.fbind
        fbind('pos', self.trigger_layout)
        fbind('children', self.trigger_layout)
        fbind('pos', self.trigger_focus_check)
        fbind('width', self.trigger_focus_check)

        Widget.__init__(self, **kwargs)

        for i in range(Config.default_beat_section_count):
            self.add_new()


    def check_focus(self, *_):
        pos = Window.mouse_pos
        for i in range(len(self.sections)):
            section = self.sections[i]
            stem = self.stems[i]  # Use top of stem as top of last bar is -inf, see do_layout
            bars = self.barss[i]

            if ((section.x - Config.section_x_buffer) <= pos[0] <= (section.right + Config.section_x_buffer) and
                    section.y <= pos[1] <= section.top) or \
               (bars.x <= pos[0] <= bars.right and section.top <= pos[1] <= (stem.top + Config.bar_top_buffer)):
                section.focused = True
                bars.focused = True
            else:
                section.focused = False
                bars.focused = False

    def add(self, committed_notes, bars, dot_number, index=0):
        section = Section(committed_notes=committed_notes)
        stem = Stem(section)
        bars = Bars(section, bars, dot_number)

        section.fbind("size", self.trigger_layout)
        section.fbind("parent_multiplier", self.trigger_layout)
        section.fbind("stem_x", self.trigger_layout)
        section.fbind("stem_bottom", self.trigger_layout)

        bars.fbind("height", self.trigger_layout)
        bars.fbind("bar_number", self.trigger_layout)
        bars.fbind("dot_width", self.trigger_layout)

        self.add_widget(section)
        self.add_widget(stem)
        self.add_widget(bars)

        self.all_sections.insert(index, section)
        self.all_barss.insert(index, bars)
        self.sections.insert(index, section)
        self.stems.insert(index, stem)
        self.barss.insert(index, bars)


    def remove(self, section, duration_till_undraw):
        """
        Stop laying section out as if this was a box layout.

        :param section: The section to be removed
        :param duration_till_undraw: The time until it is removed as a widget so isn't drawn anymore
        """
        index = self.sections.index(section)
        stem = self.stems[index]
        bars = self.barss[index]
        if len(self.sections) - 1 == index: # is last:
            bars.bar_number = 0

        self.killing.append((section, stem, bars))

        self.sections.remove(section)
        self.stems.remove(stem)
        self.barss.remove(bars)

        Clock.schedule_once(lambda _: self._remove_final(section=section, stem=stem, bars=bars), duration_till_undraw)

    def _remove_final(self, section, stem, bars):
        self.killing.remove((section, stem, bars))
        self.all_sections.remove(section)
        self.all_barss.remove(bars)

        self.remove_widget(section)
        self.remove_widget(stem)
        self.remove_widget(bars)

    def do_layout(self, *_):
        x = self.x
        for i, section in enumerate(self.all_sections):
            dot_width = self.all_barss[i].dot_width * section.parent_multiplier

            x += Config.section_x_buffer * section.parent_multiplier

            section.x = x
            section.y = self.y

            width_addition = section.width + Config.section_x_buffer * section.parent_multiplier
            if dot_width > width_addition:
                width_addition = dot_width
            x += width_addition


        section_max_height = 0
        bars_max_height = 0
        for i in range(len(self.barss)):
            if self.sections[i].height > section_max_height:
                section_max_height = self.sections[i].top

            if self.barss[i].height > bars_max_height:
                bars_max_height = self.barss[i].height


        self.width = x

        max_height = section_max_height + bars_max_height
        for i in range(len(self.stems)):
            stem = self.stems[i]
            section = self.sections[i]

            stem.x = section.x + section.stem_x
            stem.y = section.stem_bottom + section.y
            stem.height = max_height - stem.y

        for i in range(len(self.barss) - 1):
            bars = self.barss[i]

            stem = self.stems[i]
            stem2 = self.stems[i + 1]

            bars.x = stem.x
            bars.width = stem2.x - stem.x
            bars.top = max_height

        if len(self.barss) > 0:
            self.barss[-1].top = -math.inf  # Don't worry about last one, it's easier to have but shouldn't be seen

        self.height = max_height - self.y


        for (section, stem, bars) in self.killing:
            stem.x = section.x + section.stem_x
            stem.y = section.stem_bottom + section.y

            bars.x = stem.x
            bars.width = section.width
            bars.top = stem.top

    def add_new(self, after=None):
        # New section needs to have committed notes or else it will kill itself for being empty, so either default hh
        # or copy last if possible
        if after is None:
            committed_notes = [1]
            index_of_added = 0
            bars = Config.default_beat_bars
            dot_number = Config.default_beat_dot_count
        else:
            committed_notes = after.committed_notes.copy()
            index_of_after = self.sections.index(after)
            index_of_added = index_of_after + 1
            bars = self.barss[index_of_after].get_bars()
            dot_number = self.barss[index_of_after].get_dot_number()
        self.add(committed_notes, bars, dot_number, index=index_of_added)
