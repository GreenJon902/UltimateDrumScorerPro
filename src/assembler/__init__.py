from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

from assembler.pageHolder import PageHolder

Builder.load_file("assembler/assembler.kv")


class Assembler(RelativeLayout):
    pageHolders: list[PageHolder] = list()

    def __init__(self, pages_contents=None, **kwargs):
        if pages_contents is None:
            pages_contents = list()

        self.pageHolders = list()
        RelativeLayout.__init__(self, **kwargs)

        for page_contents in pages_contents:
            self.add_page(page_contents)  # Default page

    def add_page(self, contents=None):
        holder = PageHolder(contents)

        self.pageHolders.append(holder)
        self.add_widget(holder)
