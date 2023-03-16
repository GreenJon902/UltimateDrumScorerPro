from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

from assembler.pageHolder import PageHolder

Builder.load_file("assembler/assembler.kv")


class Assembler(RelativeLayout):
    pageHolders: list[PageHolder] = list()

    def __init__(self, **kwargs):
        self.pageHolders = list()
        RelativeLayout.__init__(self, **kwargs)

        self.add_page()  # Default page

    def add_page(self):
        holder = PageHolder()

        self.pageHolders.append(holder)
        self.add_widget(holder)
