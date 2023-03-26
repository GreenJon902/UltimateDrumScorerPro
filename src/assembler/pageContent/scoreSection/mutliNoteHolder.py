from kivy.clock import Clock
from kivy.uix.widget import Widget


class MultiNoteHolder(Widget):
    trigger_sizing = None
    trigger_layout = None

    def __init__(self, **kwargs):
        self.trigger_sizing = Clock.create_trigger(self.do_sizing, -1)
        self.trigger_layout = Clock.create_trigger(self.do_layout, -1)

        Widget.__init__(self, **kwargs)
        self.fbind("children", self.trigger_sizing)
        self.fbind("children", self.trigger_layout)
        self.fbind("pos", self.trigger_layout)
        self.fbind("size", self.trigger_layout)

        self.trigger_sizing()  # Which then causes layout

    def add_widget(self, widget, **kwargs):
        widget.fbind("size", self.trigger_sizing)
        Widget.add_widget(self, widget, **kwargs)

    def remove_widget(self, widget):
        widget.funbind("size", self.trigger_sizing)
        Widget.remove_widget(self, widget)

    def do_sizing(self, *_):
        width = 0
        height = 0
        for child in self.children:
            if child.width > width:
                width = child.width
            if child.height > height:
                height = child.height
        self.width = width
        self.height = height

    def do_layout(self, *_):
        for child in self.children:
            child.top = self.top
            child.right = self.right
