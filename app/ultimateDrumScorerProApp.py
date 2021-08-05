from kivy.app import App
from kivy.core.window import Window
from kivy.lang.builder import Builder

from app.boxLayoutWithEvents import BoxLayoutWithHoverEvent, BoxLayoutWithClickHoverEvent
from app.scoreView import ScoreView
from app.customMouse import CustomMouse
from logger.classWithLogger import ClassWithLogger


class UltimateDrumScorerProApp(App, ClassWithLogger):
    def build(self):
        root = Builder.load_file("resources/kv.kv")
        self.log_debug("Loaded and built KV")
        self.log_info("Built")

        return root


    def set_cursor(self, name):
        self.log_info(f"Setting cursor to {name}")

        found = Window.set_system_cursor(name)

        if not found:
            Window.show_cursor = False
            self.root.ids["custom_mouse"].name = name
            self.root.ids["custom_mouse"].show()

            self.log_debug(f"No system cursor found for {name}, trying to find a custom one")

        else:
            self.root.ids["custom_mouse"].hide()
            Window.show_cursor = True
            self.log_debug(f"System cursor found for {name}")
