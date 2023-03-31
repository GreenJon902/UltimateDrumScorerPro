from kivy.event import EventDispatcher
from kivy.properties import ListProperty, NumericProperty

from score.notes import Note


class ScoreSectionSectionStorage(EventDispatcher):
    decoration_id: int = NumericProperty(defalutvalue=None, allownone=True)
    delta_bars: int = NumericProperty(defalutvalue=0)
    before_flags: int = NumericProperty(defalutvalue=0)  # Can be just half bars
    after_flags: int = NumericProperty(defalutvalue=0)
    dots: int = NumericProperty(defalutvalue=0)
    note_ids: list[int] = ListProperty(defalutvalue=[])

    def unbind_all(self, callback):
        self.unbind(decoration_id=callback, delta_bars=callback, before_flags=callback,
                    after_flags=callback, note_ids=callback, dots=callback)

    def bind_all(self, callback):
        self.bind(decoration_id=callback, delta_bars=callback, before_flags=callback,
                  after_flags=callback, note_ids=callback, dots=callback)


class ScoreSectionStorage(EventDispatcher):
    _sections: list[ScoreSectionSectionStorage]  # Protect because of bindings
    bindings: list[callable]

    def __init__(self, sections=None, **kwargs):
        if sections is None:
            sections = []

        self.bindings = []
        self._sections = []
        self.set_sections(sections)
        EventDispatcher.__init__(self, **kwargs)

    def unbind_all(self, callback):
        self.bindings.remove(callback)
        for section in self._sections:
            section.unbind_all(callback)

    def bind_all(self, callback):
        self.bindings.append(callback)
        for section in self._sections:
            section.bind_all(callback)


    def get_section(self, index):
        return self._sections[index]

    def pop_section(self, index):
        section = self._sections.pop(index)
        for binding in self.bindings:
            section.unbind_all(binding)
        return section

    def remove_section(self, section):
        self._sections.remove(section)
        for binding in self.bindings:
            section.unbind_all(binding)

    def clear_all_sections(self):
        for section in self._sections:
            for binding in self.bindings:
                section.unbind_all(binding)
        self._sections.clear()

    def get_sections(self):
        return self._sections

    def set_sections(self, sections):
        self.clear_all_sections()
        for section in sections:
            self._sections.append(section)
            for callback in self.bindings:
                section.bind_all(callback)
        for binding in self.bindings:
            binding(self, self.get_sections())


    # Editor Settings
    normal_editor_note_ids: list[int] = ListProperty()
