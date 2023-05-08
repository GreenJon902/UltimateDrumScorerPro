from kivy.uix.widget import Widget

from renderer.text import Text_NormalRenderer


class Text_CorrectlySizedRenderer(Text_NormalRenderer):
    location: Widget  # To where this is rendered to (aka a child of some scatter)

    def __init__(self, location):
        self.location = location
        Text_NormalRenderer.__init__(self)

    def get_zoom_amount(self):
        return self.location.to_window(0, 1)[1] - self.location.to_window(0, 0)[1]

    def update_label_options(self, *args):
        Text_NormalRenderer.update_label_options(self, *args)
        self.label.options["font_size"] *= self.get_zoom_amount()

    def get_label_size(self):
        size = Text_NormalRenderer.get_label_size(self)
        zoom_amount = self.get_zoom_amount()
        return size[0] / zoom_amount, size[1] / zoom_amount
