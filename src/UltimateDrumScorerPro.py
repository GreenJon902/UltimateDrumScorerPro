from betterLogger import ClassWithLogger
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout

from beat import Beat


def run():
    print("Starting...")
    import os
    import sys
    stderr = sys.stderr

    if len(sys.argv) >= 2 and sys.argv[1].startswith("log_level="):
        os.environ["LOG_LEVEL"] = sys.argv[1].split("=")[1]

    os.environ["APPNAME"] = "UltimateDrumScorerPro"
    os.environ["APPAUTHOR"] = "GreenJon902"
    os.environ["APPVERSION"] = "v2.0"
    os.environ["SHORT_APPNAME"] = "UDSP"

    import betterLogger
    base_logger = betterLogger.get_logger("BaseLogger")

    # ==================================================================================================================

    base_logger.log_info("Setting up kivy")
    os.environ["KIVY_NO_FILELOG"] = "True"
    os.environ["KIVY_NO_CONSOLELOG"] = "True"
    os.environ["KCFG_INPUT_MOUSE"] = "mouse,multitouch_on_demand"
    base_logger.log_dump("Set ENV variables \"KIVY_NO_FILELOG\" and \"KIVY_NO_CONSOLELOG\" too True | "
                         "\"KCFG_INPUT_MOUSE\" set too \"mouse,multitouch_on_demand\"")
    # noinspection PyUnresolvedReferences
    import kivy
    from kivy.logger import Logger
    sys.stderr = stderr  # revert back # TODO: Fix this
    Logger.setLevel(betterLogger.config.log_level)
    base_logger.log_info("Set up kivy")

    # ==================================================================================================================

    base_logger.log_info("Starting...")
    root = Root()
    root.run()
    base_logger.log_info("Finished!")


class Root(ClassWithLogger, App):
    def __init__(self):
        ClassWithLogger.__init__(self, name="UI.RootWidget")
        App.__init__(self)

    def build(self):
        container = BoxLayout(pos=(100, 100))
        layout = Beat()
        container.add_widget(layout)
        with container.canvas.before:
            Color(rgb=(1, 1, 1))
            r = Rectangle(pos=(0, 0), size=container.size)
            container.bind(size=lambda _, x: setattr(r, "size", x))

        return container



if __name__ == "__main__":
    run()
