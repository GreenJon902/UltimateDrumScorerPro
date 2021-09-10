from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.graphicsConstants import tooltip_bg_color, tooltip_text_color, tooltip_padding


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
        ButtonBehavior.__init__(self, **kwargs)
        BoxLayoutWithHoverEvent.__init__(self, **kwargs)


# Inspired by https://stackoverflow.com/a/34471497
class BoxLayoutWithToolTipClickHoverEvent(BoxLayoutWithClickHoverEvent):
    tooltip: Label
    tooltip_text: str = StringProperty()

    tooltip_rect: Rectangle

    def __init__(self, **kwargs):
        BoxLayoutWithClickHoverEvent.__init__(self, **kwargs)

        self.tooltip = Label(size_hint=(None, None), color=tooltip_text_color)

        with self.tooltip.canvas.before:
            Color(rgb=tooltip_bg_color)
            self.tooltip_rect = Rectangle(pos=self.tooltip.pos, size=self.tooltip.size)



    def on_tooltip_text(self, _instance, value):
        self.tooltip.text = value
        self.tooltip.texture_update()

        self.tooltip.size = self.tooltip.texture_size[0] + tooltip_padding, \
                            self.tooltip.texture_size[1] + tooltip_padding
        self.tooltip_rect.size = self.tooltip.size


    def _mouse_move(self, _instance, pos):
        BoxLayoutWithClickHoverEvent._mouse_move(self, _instance, pos)

        Clock.unschedule(self.display_tooltip)

        self.close_tooltip()
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(lambda _elapsed_time: self.display_tooltip(pos), 1)


    def close_tooltip(self):
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, pos):
        self.tooltip.pos = pos
        self.tooltip_rect.pos = pos
        if self.tooltip not in Window.children:
            Window.add_widget(self.tooltip)


    """def _mouse_move(self, _instance, pos):
        BoxLayoutWithClickHoverEvent._mouse_move(self, _instance, pos)

        self.tooltip.pos = pos
        Clock.unschedule(self.display_tooltip)

        if self.tooltip in Window.children:
            self.close_tooltip()

        if self.collide_point(*pos):
            Clock.schedule_once(lambda _elapsed_time: self.display_tooltip(), 0.1)

    def close_tooltip(self):
        print(f"Hide - {self.tooltip_text} - {hex(id(self))}")
        Window.remove_widget(self.tooltip)

    def display_tooltip(self):
        print(f"Show - {self.tooltip_text} - {hex(id(self))}")

        self.tooltip.text = self.tooltip_text

        Clock.schedule_once(lambda _elapsed_time: self._display_tooltip(), 0)

    def _display_tooltip(self):
        self.tooltip.size = self.tooltip.texture_size[0] + tooltip_padding, \
                            self.tooltip.texture_size[1] + tooltip_padding
        self.tooltip_rect.pos = self.tooltip.pos
        self.tooltip_rect.size = self.tooltip.size

        if self.tooltip not in Window.children:
            Window.add_widget(self.tooltip)"""
