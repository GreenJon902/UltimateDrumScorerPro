from kivy.event import EventDispatcher
from kivy.properties import ListProperty, NumericProperty, BooleanProperty

from score.notes import Note


class ScoreSectionSectionStorage(EventDispatcher):
    decoration_id: int = NumericProperty(defalutvalue=None, allownone=True)
    bars: int = NumericProperty(defalutvalue=0)
    before_flags: int = NumericProperty(defalutvalue=0)  # Half bars
    after_flags: int = NumericProperty(defalutvalue=0)
    slanted_flags: int = NumericProperty(defalutvalue=0)
    dots: int = NumericProperty(defalutvalue=0)
    note_ids: list[int] = ListProperty(defalutvalue=[])

    binding_groups: dict[callable, list[tuple[str, callable]]]
    def __init__(self, **kwargs):
        self.binding_groups = {}
        EventDispatcher.__init__(self, **kwargs)

    def bind_all(self, callback):
        if callback not in self.binding_groups:
            binding_group = [
                ("decoration_id", lambda *_: callback("section", "decoration_id", self)),
                ("bars", lambda *_: callback("section", "bars", self)),
                ("before_flags", lambda *_: callback("section", "before_flags", self)),
                ("after_flags", lambda *_: callback("section", "after_flags", self)),
                ("slanted_flags", lambda *_: callback("section", "slanted_flags", self)),
                ("note_ids", lambda *_: callback("section", "note_ids", self)),
                ("dots", lambda *_: callback("section", "dots", self))
            ]
            self.binding_groups[callable] = binding_group
            for binding in binding_group:
                self.fbind(binding[0], binding[1])

    def unbind_all(self, callback):
        if callback in self.binding_groups:
            self.binding_groups.pop(callback)
            for binding in self.binding_groups[callback]:
                self.funbind(binding[0], binding[1])


class ScoreSectionStorage(EventDispatcher):
    _sections: list[ScoreSectionSectionStorage]  # Protect because need to be bound
    callbacks: list[callable]
    dot_callbacks: dict[callable]

    dots_at_top: int = BooleanProperty(defalutvalue=False)

    def __init__(self, sections=None, **kwargs):
        if sections is None:
            sections = []

        self.callbacks = []
        self.dot_callbacks = {}
        self._sections = []
        self.set(sections)
        EventDispatcher.__init__(self, **kwargs)


    def bind_all(self, callback):
        self.callbacks.append(callback)
        for section in self._sections:
            section.bind_all(callback)
        if callback not in self.dot_callbacks:
            self.dot_callbacks[callback] = lambda *_: callback("storage", "dots_at_top", self)
            self.fbind("dots_at_top", self.dot_callbacks[callback])

    def unbind_all(self, callback):
        for section in self._sections:
            section.unbind_all(callback)
        self.callbacks.remove(callback)
        if callback in self.dot_callbacks:
            self.funbind("dots_at_top", self.dot_callbacks[callback])
            self.dot_callbacks.pop(callback)

    def _clear_bindings(self):  # But doesn't delete from callbacks list
        for callback in self.callbacks:
            for section in self._sections:
                section.unbind_all(callback)

    def _rebind_bindings(self):  # But doesn't add to list and expects no bindings
        for callback in self.callbacks:
            for section in self._sections:
                section.bind_all(callback)


    def append(self, section):
        self.insert(len(self), section)

    def insert(self, index, section):
        self._sections.insert(index, section)
        for callback in self.callbacks:
            section.bind_all(callback)
            callback("storage", "insert", index)

    def pop(self, index=None):
        if index is None:
            index = len(self._sections) - 1  # Last item
        section = self._sections.pop(index)
        for callback in self.callbacks:
            section.unbind_all(callback)
            callback("storage", "remove", index)
        return section

    def remove(self, section):
        self.pop(self._sections.index(section))

    def set(self, sections):
        self._clear_bindings()
        self._sections = sections
        self._rebind_bindings()
        for callback in self.callbacks:
            callback("storage", "set")

    def index(self, section):
        return self._sections.index(section)


    def __len__(self):
        return len(self._sections)

    def __iter__(self):
        return SectionIterator(self)

    def __getitem__(self, index):
        return self._sections[index]


    # Editor Settings
    normal_editor_note_ids: list[int] = ListProperty()


class SectionIterator:
    scoreSectionStorage: ScoreSectionStorage
    index: int

    def __init__(self, scoreSectionStorage):
        self.scoreSectionStorage = scoreSectionStorage
        self.index = 0

    def __next__(self):
        if self.index < len(self.scoreSectionStorage):
            value = self.scoreSectionStorage[self.index]
            self.index += 1
            return value
        else:
            raise StopIteration
