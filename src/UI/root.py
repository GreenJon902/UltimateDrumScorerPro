from betterLogger import ClassWithLogger
from kivy.app import App


class Root(ClassWithLogger, App):
    def __init__(self):
        ClassWithLogger.__init__(self, name="UI.RootWidget")
        App.__init__(self)
