from kivy.uix.relativelayout import RelativeLayout


class PageContents(RelativeLayout):
    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        self.size_hint = None, None
        self.size = 210, 297  # A4 in mm
