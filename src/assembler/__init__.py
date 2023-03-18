from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

from assembler.pageHolder import PageHolder

Builder.load_file("assembler/assembler.kv")


class Assembler(RelativeLayout):
    pageHolders: list[PageHolder]

    def __init__(self, pages_contents=None, **kwargs):
        if pages_contents is None:
            pages_contents = [[]]

        self.pageHolders = []
        RelativeLayout.__init__(self, **kwargs)

        for page_content in pages_contents:
            self.add_page(page_content)  # Default page
        self.set_current_page(0)

    def add_page(self, contents=None):
        holder = PageHolder(contents)

        self.pageHolders.append(holder)

    def set_current_page(self, page_number):
        self.clear_widgets()
        self.add_widget(self.pageHolders[page_number])
