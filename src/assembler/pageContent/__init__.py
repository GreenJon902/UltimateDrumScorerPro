from __future__ import annotations

import math
import typing

from kivy import metrics
from kivy.core.window import Window
from kivy.input import MotionEvent
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

if typing.TYPE_CHECKING:
    from editor import Editor

Builder.load_file("assembler/pageContent/pageContent.kv")


class PageContent(RelativeLayout):
    editor: Editor

    def __init__(self, editor, **kwargs):
        self.editor = editor
        RelativeLayout.__init__(self, **kwargs)


    def on_touch_down(self, touch: MotionEvent):
        if self.collide_point(touch.x, touch.y) and self.editor.has_selected(self):
            touch.grab(self, exclusive=True)
            return True

    def on_touch_move(self, touch: MotionEvent):
        if touch.grab_current == self:
            self.x += touch.dx
            self.y += touch.dy

    def on_touch_up(self, touch: MotionEvent):
        overall_change_x = (touch.sx - touch.osx) * Window.width  # So in physical px ( not transformed )
        overall_change_y = (touch.sy - touch.osy) * Window.height  # So in physical px ( not transformed )
        overall_change = math.sqrt(overall_change_x ** 2 + overall_change_y ** 2)

        if self.collide_point(touch.x, touch.y) and overall_change < metrics.mm(1):
            # If within bounds and moved under 1 mm and nothing else has grabbed it
            print(f"{self} clicked on.")

            if self.editor.has_selected(self):
                self.editor.select(None)
            else:
                self.editor.select(self)
            return True
