from kivy.uix.label import Label

from assembler.pageContent import PageContent


class Text(PageContent):
    def __init__(self, text, **kwargs):
        PageContent.__init__(self, **kwargs)
        self.add_widget(Label(text=text, color=(0, 0, 0, 1)))
