from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

from assembler.page import Page

Builder.load_file("assembler/assembler.kv")


class Assembler(RelativeLayout):
    page: Page

    def __init__(self, **kwargs):
        self.page = Page()
        RelativeLayout.__init__(self, **kwargs)
        self.add_widget(self.page)
