from kivy.app import App
from kivy.core.window import Window

from assembler import Assembler
from assembler.pageContent.text import Text


def run():
    print("Starting...")
    import os

    os.environ["APPNAME"] = "UltimateDrumScorerPro"
    os.environ["APPAUTHOR"] = "GreenJon902"
    os.environ["APPVERSION"] = "v3.0"
    os.environ["SHORT_APPNAME"] = "UDSP"

    # ==================================================================================================================

    print("Setting up kivy...")
    os.environ["KCFG_INPUT_MOUSE"] = "mouse,multitouch_on_demand"
    # noinspection PyUnresolvedReferences
    import kivy

    # ==================================================================================================================

    print("Starting...")
    root = Root()
    root.run()
    print("Finished!")


class Root(App):
    def __init__(self):
        App.__init__(self)

    def build(self):
        assembler = Assembler(
           [
               [
                   Text("test")
               ]
           ]
        )
        Window.bind(size=lambda _, size: self.update_size(assembler, size))

        return assembler

    def update_size(self, widget, size):
        widget.size = size


if __name__ == "__main__":
    run()
