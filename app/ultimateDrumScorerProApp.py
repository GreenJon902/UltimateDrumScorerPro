from kivy.app import App
from kivy.lang.builder import Builder

from app.boxLayoutWithEvents import BoxLayoutWithHoverEvent
from logger.classWithLogger import ClassWithLogger


class UltimateDrumScorerProApp(App, ClassWithLogger):
    def build(self):
        root = Builder.load_file("resources/kv.kv")
        self.log_debug("Loaded and built KV")
        self.log_info("Built")

        return root
