from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget


class MultiBarHolder(Widget):  # Like multi note holder but parent sets width
    highest_line: int = NumericProperty()
    trigger_layout = None

    def __init__(self, **kwargs):
        self.trigger_layout = Clock.create_trigger(self.do_layout, -1)

        Widget.__init__(self, **kwargs)
        self.fbind("children", self.trigger_layout)
        self.fbind("pos", self.trigger_layout)
        self.fbind("size", self.trigger_layout)

        self.trigger_layout()

    def do_layout(self, *_):
        y = self.y
        for child in self.children:
            child.width = self.width
            child.right = self.right
            child.y = y
            y += child.height
        self.height = y

        if len(self.children) > 0:
            self.highest_line = self.height - self.children[-1].height + self.children[-1].line_height
        else:
            self.highest_line = 0

