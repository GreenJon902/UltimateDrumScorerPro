from kivy.clock import Clock
from kivy.tests.common import GraphicUnitTest
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter

from renderer.text import TextRenderer, Text_MarkdownFormatter, Text_ColorFormatter, Text_NormalRenderer
from renderer.text.text_correctlySizedRenderer import Text_CorrectlySizedRenderer
from scoreStorage.textStorage import TextStorage


class TextTestCases(GraphicUnitTest):
    def test_text(self):
        storage = TextStorage(text="*hi* **how** __are__ _you_ &#aaffaa~~today~~")
        text_renderer = TextRenderer(storage, formatters=[Text_MarkdownFormatter(), Text_ColorFormatter()],
                                     size_hint=(None, None))
        # noinspection PyProtectedMember
        Clock.schedule_once(lambda _: print(text_renderer._formatted_text), -1)
        text_renderer.renderer = Text_NormalRenderer()

        scatter = Scatter()
        scatter.scale = 10
        scatter.pos = 0, text_renderer.top
        text_renderer.bind(top=lambda _, value: setattr(scatter, "y", value))
        storage2 = TextStorage(text="*hi* **how** __are__ _you_ &#aaffaa~~today~~", font_size=1)
        text_renderer2 = TextRenderer(storage2, formatters=[Text_MarkdownFormatter(), Text_ColorFormatter()])
        text_renderer2.renderer = Text_CorrectlySizedRenderer(text_renderer2)
        scatter.add_widget(text_renderer2)

        container = FloatLayout()
        container.add_widget(text_renderer)
        container.add_widget(scatter)

        self.render(container)
