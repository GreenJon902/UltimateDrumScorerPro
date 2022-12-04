from typing import Union, Callable

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.graphics import Color
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.widget import Widget

from config.config import Config


class CommittableButtonInfo(EventDispatcher):
    widget: Widget
    color: Union[Color, ColorProperty]
    collide_func: Callable[[tuple[int, int]], tuple[bool, int]]

    final_transparency_multiplier_name: str
    committed_name: str
    configurableness_name: str

    transparency: int = NumericProperty()

    def __init__(self, handler, widget: Widget, color: Union[Color, ColorProperty],
                 collide_func: Callable[[tuple[int, int]], tuple[bool, int]], final_transparency_multiplier_name,
                 committed_name, configurableness_name):
        self.trigger_recalculate_transparency = Clock.create_trigger(self.calculate_transparency, -1)

        self.handler = handler
        self.widget = widget
        self.color = color
        self.collide_func = collide_func
        self.final_transparency_multiplier_name = final_transparency_multiplier_name
        self.committed_name = committed_name
        self.configurableness_name = configurableness_name

        widget.fbind("pos", handler.trigger_recalculation)
        self.fbind("transparency", self.trigger_recalculate_transparency)
        widget.fbind(final_transparency_multiplier_name, self.trigger_recalculate_transparency)
        widget.fbind(configurableness_name, self.trigger_recalculate_transparency)
        widget.fbind(committed_name, self.on_committed)

    def on_committed(self, *_):
        transparency = 1 if getattr(self.widget, self.committed_name) else Config.uncommitted_transparency
        a = Animation(transparency=transparency, duration=Config.commit_speed)
        a.start(self)

    def calculate_transparency(self, *_):
        self.color.a = self.transparency * \
                       (1 if getattr(self.widget, self.committed_name) else
                        getattr(self.widget, self.configurableness_name)) * \
                       getattr(self.widget, self.final_transparency_multiplier_name)


def recolor_info(info):
    committed = getattr(info.widget, info.committed_name)
    a = Animation(r=(Config.committed_hover_color[0] if committed else
                     Config.uncommitted_hover_color[0]),
                  b=(Config.committed_hover_color[1] if committed else
                     Config.uncommitted_hover_color[1]),
                  g=(Config.committed_hover_color[2] if committed else
                     Config.uncommitted_hover_color[2]),
                  duration=Config.hover_color_fade_speed)
    a.start(info.color)


class CommittableButtonHandler_:
    registered: list[CommittableButtonInfo]
    current_hover: Union[None, CommittableButtonInfo]

    def __init__(self):
        self.registered = list()
        self.current_hover = None

        self.trigger_recalculation = Clock.create_trigger(self._recalculate, -1)

        Window.bind(mouse_pos=self.trigger_recalculation)
        Window.bind(on_touch_up=self.on_click)


    def _recalculate(self, *_):
        collided = self.get_current_collided()
        if self.current_hover != collided:
            if self.current_hover is not None:
                a = Animation(r=0, b=0, g=0, duration=Config.hover_color_fade_speed)
                a.start(self.current_hover.color)
                self.current_hover = None

            if collided is not None:
                recolor_info(collided)
                self.current_hover = collided

    def on_click(self, *_):
        collided = self.get_current_collided()
        if collided is not None:
            setattr(collided.widget, collided.committed_name, not getattr(collided.widget, collided.committed_name))
            recolor_info(collided)


    def get_current_collided(self) -> Union[None, CommittableButtonInfo]:
        pos = Window.mouse_pos
        collided = None
        for info in self.registered:
            collision_info = info.collide_func(pos)
            if collision_info[0]:
                if collided is None:
                    collided = (info, collision_info[1])
                elif collision_info[1] < collided[1]:
                    collided = (info, collision_info[1])
        return collided[0] if collided is not None else None




    def register(self, widget: Widget, color: Union[Color, ColorProperty],
                 collide_func: Callable[[tuple[int, int]], tuple[bool, int]], final_transparency_multiplier_name,
                 committed_name, configurableness_name):
        info = CommittableButtonInfo(self, widget, color, collide_func, final_transparency_multiplier_name,
                                     committed_name, configurableness_name)
        self.registered.append(info)


CommittableButtonHandler = CommittableButtonHandler_()
