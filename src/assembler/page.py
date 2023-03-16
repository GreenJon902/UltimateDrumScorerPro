from kivy.uix.relativelayout import RelativeLayout

from assembler.pageContents import PageContents


class Page(RelativeLayout):
    pageContents: PageContents

    def __init__(self, **kwargs):
        self.pageContents = PageContents()
        RelativeLayout.__init__(self, **kwargs)
        self.add_widget(self.pageContents)
