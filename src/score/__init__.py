from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, ListProperty, NumericProperty


class ScoreSectionSectionStorage(EventDispatcher):
    decoration_id: int = NumericProperty(defalutvalue=None, allownone=True)
    bars: int = NumericProperty(defalutvalue=0)
    dots: int = NumericProperty(defalutvalue=0)
    note_ids: list[int] = ListProperty(defalutvalue=[])

    def unbind_all(self, callback):
        self.unbind(decoration_id=callback, bars=callback, note_ids=callback, dots=callback)

    def bind_all(self, callback):
        self.bind(decoration_id=callback, bars=callback, note_ids=callback, dots=callback)


class ScoreSectionStorage(EventDispatcher):
    sections: list[ScoreSectionSectionStorage]
    bindings: list[EventDispatcher]

    def __init__(self, sections=None, **kwargs):
        if sections is None:
            sections = []

        self.bindings = []
        self.sections = sections
        EventDispatcher.__init__(self, **kwargs)

    def unbind_all(self, callback):
        self.bindings.remove(callback)
        for section in self.sections:
            section.unbind_all(callback)

    def bind_all(self, callback):
        self.bindings.append(callback)
        for section in self.sections:
            section.bind_all(callback)


    def get_section(self, index):
        return self.sections[index]

    def pop_section(self, index):
        section = self.sections.pop(index)
        for binding in self.bindings:
            section.unbind_all(binding)
        return section

    def remove_section(self, section):
        self.sections.remove(section)
        for binding in self.bindings:
            section.unbind_all(binding)

    def clear_all_sections(self):
        for section in self.sections:
            for binding in self.bindings:
                section.unbind_all(binding)
        self.sections.clear()
