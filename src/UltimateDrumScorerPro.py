from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from assembler import Assembler
from assembler.pageContent.text import Text
from editor import Editor


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
    Builder.load_file("misc.kv")

    # ==================================================================================================================

    print("Starting...")
    root = UltimateDrumScorerProApp()
    root.run()
    print("Finished!")


class UltimateDrumScorerProApp(App):
    def __init__(self):
        App.__init__(self)

    def build(self):
        boxLayout = BoxLayout(orientation="vertical")
        editor = Editor()
        boxLayout.add_widget(Assembler(
               [
                   [
                       Text(editor, text="*hi* **how** __are__ _you_", pos=(210 / 2, 297 / 2))
                   ]
               ]
            )
        )
        boxLayout.add_widget(editor)
        Window.bind(size=lambda _, size: self.update_size(boxLayout, size))

        return boxLayout

    def update_size(self, widget, size):
        widget.size = size


if __name__ == "__main__":
    run()
