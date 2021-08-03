from kivy.app import App
from kivy.lang.builder import Builder


class UltimateDrumScorerProApp(App):
    def build(self):
        return Builder.load_file("resources/kv.kv")
