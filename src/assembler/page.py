from kivy.uix.relativelayout import RelativeLayout

from assembler.pageContent import PageContent


class Page(RelativeLayout):
    contents: list[PageContent]

    def __init__(self, contents=None, **kwargs):
        if contents is None:
            contents = list()
        self.contents = contents

        RelativeLayout.__init__(self, **kwargs)
        self.size_hint = None, None
        self.size = 210, 297  # A4 in mm

        for content in contents:
            self.add_widget(content)
