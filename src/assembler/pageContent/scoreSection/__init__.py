from typing import Optional

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.button import Button

from assembler.pageContent import PageContent
from score import ScoreSectionStorage
from score.notes import notes
from selfSizingBoxLayout import SelfSizingBoxLayout


class ScoreSection(PageContent):
    score: ScoreSectionStorage = ObjectProperty(defaultvalue=ScoreSectionStorage())
    _old_score: Optional[ScoreSectionStorage] = None

    container: SelfSizingBoxLayout  # Holes everything
    bottomContainer: SelfSizingBoxLayout  # Note heads and decoration
    topContainer: SelfSizingBoxLayout  # Bars
    update = None

    def __init__(self, *args, **kwargs):
        self.update = Clock.create_trigger(self._update, -1)
        self.container = SelfSizingBoxLayout(orientation="vertical")
        self.bottomContainer = SelfSizingBoxLayout(orientation="horizontal", anchor="highest")
        self.topContainer = SelfSizingBoxLayout(orientation="horizontal", anchor="lowest")
        self.container.add_widget(self.bottomContainer)
        self.container.add_widget(self.topContainer)

        PageContent.__init__(self, *args, **kwargs)

        self.container.bind(size=self.on_container_size)

        self.add_widget(self.container)
        self.on_score(self, self.score)

    def on_score(self, _, value):
        if self._old_score is not None:
            self._old_score.unbind_all(self.update)

        self._old_score = value
        value.bind_all(self.update)

        self.update()

    def on_container_size(self, _, value):
        self.size = value

    def _update(self, *_):
        print(f"Redrawing {self}")

        for section in self.score.sections:
            for note_id in section.note_ids:
                note = notes[note_id]()
                note.height = note.drawing_height + 40 + note.note_level * -20

                self.bottomContainer.add_widget(note, index=len(self.bottomContainer.children))
