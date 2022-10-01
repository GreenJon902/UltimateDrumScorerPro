from betterLogger import ClassWithLogger
from kivy.app import App
from kivy.graphics import Rectangle, Color
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatterlayout import *
from kivy.lang.builder import Builder

import UltimateDrumScorerPro
from UI.scoreElements.notationElement.notationElement import NotationElement
from UI.scoreElements.notationElement.notationRenderer import drawBeatContents
from config.notationConfig import NotationRendererConfig
from notationTree import Bar, Notes, MultipleNotes


class Root(ClassWithLogger, App):
    def __init__(self):
        ClassWithLogger.__init__(self, name="TestCases.BasicEditingAndRendering.RootWidget")
        App.__init__(self)

    def build(self):
        root = FloatLayout()
        with root.canvas.before:
            Color(rgb=(1, 1, 1))
            r = Rectangle(pos=root.pos, size=root.size)

            def update(*args):
                r.size = root.size

            root.bind(size=update)

        scatterLayout = ScatterPlaneLayout()
        root.add_widget(scatterLayout)
        with scatterLayout.canvas:
            drawBeatContents(MultipleNotes([Notes("kick"), Notes("snare")]).flatten(), NotationRendererConfig())
        return root


if __name__ == "__main__":
    UltimateDrumScorerPro.prepare()
    root = Root()
    root.run()
