from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout

from kv import check_kv

check_kv()


class Decoration(RelativeLayout):
    min_height: int = NumericProperty()
    container_height: int = NumericProperty(allownone=True, defualtvalue=None)  # Height of container, e.g. the
                                                                                # entire scoreStorage
    _container_height: float = NumericProperty()

    def __init__(self, **kwargs):
        kwargs.setdefault("container_height", None)  # Ye so this is necessary.
        RelativeLayout.__init__(self, **kwargs)
        self.height = self.min_height
        self.canvas.opacity = 1

    def on_height(self, _, value):
        if value < self.min_height:
            self.height = self.min_height
        self.on_container_height(self, self.container_height)

    def on_container_height(self, _, value):
        if value is None:
            self._container_height = self.height
        else:
            self._container_height = value

    def on_min_height(self, _, value):
        if self.height < value:
            self.height = value
