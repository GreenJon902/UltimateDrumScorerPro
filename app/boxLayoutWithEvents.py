from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout


class BoxLayoutWithHoverEvent(BoxLayout):
    mouse_over = BooleanProperty(False)

    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        self.register_event_type("on_mouse_enter")
        self.register_event_type("on_mouse_leave")

        Window.bind(mouse_pos=self._mouse_move)


    def _mouse_move(self, _instance, pos):
        if self.collide_point(*pos):
            self.mouse_over = True

        else:
            self.mouse_over = False


    def on_mouse_over(self, _instance, value):
        if value:
            self.dispatch("on_mouse_enter", self)

        else:
            self.dispatch("on_mouse_leave", self)


    def on_mouse_enter(self, _instance):
        pass

    def on_mouse_leave(self, _instance):
        pass



class BoxLayoutWithClickHoverEvent(ButtonBehavior, BoxLayoutWithHoverEvent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
