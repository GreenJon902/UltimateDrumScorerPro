from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter

from logger import ClassWithLogger


class CustomMouse(Scatter, ClassWithLogger):
    image: Image
    active: bool
    mouse_in_window: bool

    name: str = StringProperty()

    def __init__(self, **kwargs):
        Scatter.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        Window.bind(mouse_pos=lambda _instance, value: self._move_to(value),
                    on_cursor_enter=lambda _instance: self._show(),
                    on_cursor_leave=lambda _instance: self._hide())

        self.image = Image(opacity=0)
        self.add_widget(self.image)

        self.active = False
        self.mouse_in_window = False

    def on_name(self, _instance, value):
        self.image.source = f"resources/cursors/{value}.png"

    def _move_to(self, pos):
        self.image.center = pos

    def _show(self):
        if self.active:
            self.image.opacity = 1

        else:
            self.image.opacity = 0

        self.mouse_in_window = True

    def _hide(self):
        self.mouse_in_window = False
        self.image.opacity = 0


    def show(self):
        self.log_dump("Showing mouse")

        if self.mouse_in_window:
            self.image.opacity = 1

        else:
            self.image.opacity = 0

        self.active = True

    def hide(self):
        self.log_dump("Hiding mouse")

        self.active = False
        self.image.opacity = 0