from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

from assembler.pageContent.scoreSection import ScoreSection
from assembler.pageContent.text import Text
from assembler.pageHolder import PageHolder
from score import ScoreSectionStorage, TextStorage

Builder.load_file("assembler/assembler.kv")


class Assembler(RelativeLayout):
    pageHolders: list[PageHolder]

    def __init__(self, editor, score=None, **kwargs):
        if score is None:
            score = [[]]

        pages_contents = [[] for i in range(len(score))]
        for i, page in enumerate(score):
            for scoreStorage in page:
                t = type(scoreStorage)
                if t == ScoreSectionStorage:
                    pageContent = ScoreSection(scoreStorage, editor)
                elif t == TextStorage:
                    pageContent = Text(scoreStorage, editor)
                else:
                    raise RuntimeError()

                pages_contents[i].append(pageContent)

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
