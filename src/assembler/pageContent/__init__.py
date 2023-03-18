from __future__ import annotations

import math
import typing

from kivy import metrics
from kivy.core.window import Window
from kivy.input import MotionEvent
from kivy.uix.relativelayout import RelativeLayout

if typing.TYPE_CHECKING:
    from editor import Editor


class PageContent(RelativeLayout):
    editor: Editor

    def __init__(self, editor, **kwargs):
        self.editor = editor
        RelativeLayout.__init__(self, **kwargs)

    def on_touch_up(self, touch: MotionEvent):
        overall_change_x = (touch.sx - touch.osx) * Window.width  # So in physical px ( not transformed )
        overall_change_y = (touch.sy - touch.osy) * Window.height  # So in physical px ( not transformed )
        overall_change = math.sqrt(overall_change_x ** 2 + overall_change_y ** 2)

        if self.collide_point(touch.x, touch.y) and overall_change < metrics.mm(1) and touch.grab_current is None:
            # If within bounds and moved under 1 mm and nothing else has grabbed it
            print(f"{self} clicked on.")

            if self.editor.has_selected(self):
                self.editor.select(None)
            else:
                self.editor.select(self)
            return True
