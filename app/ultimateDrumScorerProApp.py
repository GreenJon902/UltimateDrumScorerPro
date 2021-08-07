from kivy.app import App
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty

# noinspection PyUnresolvedReferences
from app.boxLayoutWithEvents import BoxLayoutWithHoverEvent, BoxLayoutWithClickHoverEvent
# noinspection PyUnresolvedReferences
from app.customMouse import CustomMouse
# noinspection PyUnresolvedReferences
from app.graphicsConstants import sidebar_button_name_to_cursor
# noinspection PyUnresolvedReferences
from app.scoreView import ScoreView
# noinspection PyUnresolvedReferences
from logger.classWithLogger import ClassWithLogger


class UltimateDrumScorerProApp(App, ClassWithLogger):
    sidebar_button_current = ObjectProperty(None, allownone=True)


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


    def sidebar_button_clicked(self, obj):
        if self.sidebar_button_current is not None:
            self.sidebar_button_current.ids.image.source = \
                f"resources/buttons/{self.sidebar_button_current.name}_button_normal.png"
        self.sidebar_button_current = obj





    def on_sidebar_button_current(self, _instance, value):
        if value is None:
            self.set_cursor(sidebar_button_name_to_cursor[str(value)])

        else:
            button = value
            self.set_cursor(sidebar_button_name_to_cursor[str(button.name)])


    def discard_click_mode(self):
        self.sidebar_button_current.ids.image.source = f"resources/buttons/{self.sidebar_button_current.name}_button_normal.png"
        self.sidebar_button_current = None
