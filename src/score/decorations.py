from kivy.factory import Factory
from kivy.lang import Builder, global_idmap
from kivy.properties import NumericProperty, ColorProperty
from kivy.uix.relativelayout import RelativeLayout

Builder.load_file("score/decorations.kv")


class Decoration(RelativeLayout):
    color = ColorProperty(defaultvalue=(0, 0, 0, 1))
    min_height: int = NumericProperty()
    container_height: int = NumericProperty()  # Height of container, e.g. the entire score

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        self.height = self.min_height
        self.canvas.opacity = 1

    def on_height(self, _, value):
        if value < self.min_height:
            self.height = self.min_height

    def on_min_height(self, _, value):
        if self.height < value:
            self.height = value


decorations: dict[int, type[Decoration]] = {}
for (id, decoration_name) in global_idmap["decorations"].items():
    decorations[id] = Factory.get(decoration_name)
