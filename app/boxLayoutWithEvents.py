from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout


class BoxLayoutWithHoverEvent(BoxLayout):
    is_mouse_over = BooleanProperty(False)

    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        self.register_event_type("on_mouse_enter")
        self.register_event_type("on_mouse_leave")

        Window.bind(mouse_pos=self._mouse_move)


    def _mouse_move(self, _instance, pos):
        if self.collide_point(*pos):
            self.is_mouse_over = True

        else:
            self.is_mouse_over = False


    def on_is_mouse_over(self, _instance, value):
        if value:
            self.dispatch("on_mouse_enter", self)

        else:
            self.dispatch("on_mouse_leave", self)


    def on_mouse_enter(self, _instance):
        pass

    def on_mouse_leave(self, _instance):
        pass
