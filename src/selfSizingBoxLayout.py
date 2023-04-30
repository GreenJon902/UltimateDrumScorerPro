from kivy.clock import Clock
from kivy.properties import OptionProperty
from kivy.uix.widget import Widget


class SelfSizingBoxLayout(Widget):
    orientation = OptionProperty("horizontal", options=("horizontal", "vertical"))
    anchor = OptionProperty("middle", options=("lowest", "middle", "highest"))

    trigger_layout = None
    attr_names_for_vertical = {
        "lowest": "x",
        "middle": "center_x",
        "highest": "right",
    }
    attr_names_for_horizontal = {
        "lowest": "y",
        "middle": "center_y",
        "highest": "top",
    }

    def __init__(self, **kwargs):
        self.trigger_layout = Clock.create_trigger(self.do_layout, -1)

        Widget.__init__(self, **kwargs)
        self.fbind("orientation", self.trigger_layout)
        self.fbind("children", self.trigger_layout)
        self.fbind("pos", self.trigger_layout)
        self.trigger_layout()

    def do_layout(self, *_):
        if self.orientation == "vertical":
            self.width = 0
            y = 0
            for child in self.children:
                child.y = y + self.y
                y += child.height

                if child.width > self.width:
                    self.width = child.width
            self.height = y
            print(1, self.width)

            # Calculate width first as might need that for x coords
            attr_name = self.attr_names_for_vertical[self.anchor]
            for child in self.children:
                setattr(child, attr_name, getattr(self, attr_name))

        else:
            self.height = 0
            x = 0
            for child in self.children:
                child.x = x + self.x
                x += child.width

                if child.height > self.height:
                    self.height = child.height
            self.width = x

            # Calculate height first as might need that for y coords
            attr_name = self.attr_names_for_horizontal[self.anchor]
            for child in self.children:
                setattr(child, attr_name, getattr(self, attr_name))


    def add_widget(self, widget, **kwargs):
        widget.fbind("size", self.trigger_layout)
        Widget.add_widget(self, widget, **kwargs)

    def remove_widget(self, widget):
        widget.funbind("size", self.trigger_layout)
        Widget.remove_widget(self, widget)


if __name__ == "__main__":
    from random import randint
    from kivy.lang import Builder
    from kivy.uix.button import Button
    import kivy.base

    container = Builder.load_string(""" 
Widget:
    SelfSizingBoxLayout:
        id: a
        x: 0
        orientation: "horizontal"
        anchor: "lowest"
    SelfSizingBoxLayout:
        id: b
        x: a.right
        orientation: "horizontal"
        anchor: "middle"
    SelfSizingBoxLayout:
        id: c
        x: b.right
        orientation: "horizontal"
        anchor: "highest"
    SelfSizingBoxLayout:
        id: d
        x: c.right
        orientation: "vertical"
        anchor: "lowest"
    SelfSizingBoxLayout:
        id: e
        x: d.right
        orientation: "vertical"
        anchor: "middle"
    SelfSizingBoxLayout:
        id: f
        x: e.right
        orientation: "vertical"
        anchor: "highest"

""")  # So positions are all bound together


    x = 0
    for layout in container.children:
        layout.add_widget(Button(width=randint(20, 100), height=randint(20, 100)))
        layout.add_widget(Button(width=randint(20, 100), height=randint(20, 100)))
        layout.add_widget(Button(width=randint(20, 100), height=randint(20, 100)))

    kivy.base.runTouchApp(container)
