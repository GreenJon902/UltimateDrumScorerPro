from __future__ import annotations

import typing
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

from UI.scoreElements.notationElement.notationRenderer import renderLine
from UI.scoreElements.scoreElement import ScoreElement
from config.notationConfig import NotationRendererConfig
from notationTree import Bar

if typing.TYPE_CHECKING:

    from typing import Callable
    from kivy.graphics.instructions import Canvas


class NotationElement(ScoreElement, Widget):
    rendererConfig: NotationRendererConfig = ObjectProperty(NotationRendererConfig())  # default renderer config

    _content: list[Bar]

    def __init__(self, content=None, **kwargs):
        ScoreElement.__init__(self)
        Widget.__init__(self, **kwargs)

        if content is None:
            content = [
                Bar.empty(4, 4),
            ]

        self._content = content

        self.canvas.add(renderLine(content, self.rendererConfig))
        self.canvas.ask_update()
