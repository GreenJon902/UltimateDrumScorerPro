from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty

# noinspection PyUnresolvedReferences
from app.globalBindings import GlobalBindings
from app.graphicsConstants import sidebar_button_name_to_cursor
# noinspection PyUnresolvedReferences
from app.uix.boxLayoutWithEvents import BoxLayoutWithHoverEvent, BoxLayoutWithClickHoverEvent
# noinspection PyUnresolvedReferences
from app.uix.customMouse import CustomMouse
# noinspection PyUnresolvedReferences
from app.uix.scoreView import ScoreView
# noinspection PyUnresolvedReferences
from app.uix.sliderWithText import SliderWithText
from logger import ClassWithLogger


class UltimateDrumScorerProApp(App, ClassWithLogger):
    sidebar_button_current = ObjectProperty(None, allownone=True)
    current_cursor: str = "arrow"


    def build(self):
        GlobalBindings.bind(sidebar_button_clicked=self.sidebar_button_clicked)

        root = Builder.load_file("resources/kv.kv")

        self.log_debug("Loaded and built KV")
        self.log_info("Built")

        return root





    def sidebar_button_clicked(self, obj):
        self.log_dump(f"Sidebar button {obj} - {obj.name} - clicked")

        if self.sidebar_button_current is not None:
            self.sidebar_button_current.ids.image.source = \
                f"atlas://resources/atlases/buttons/{self.sidebar_button_current.name}_button_normal"
        self.sidebar_button_current = obj





    def on_sidebar_button_current(self, _instance, value):
        if value is None:
            GlobalBindings.dispatch("set_cursor", sidebar_button_name_to_cursor[str(value)])

        else:
            button = value
            GlobalBindings.dispatch("set_cursor", sidebar_button_name_to_cursor[str(button.name)])

            if button.name == "move":
                self.root.ids["score_view"].set_scroll_view_scroll_mode(["content", "bars"])

            else:
                self.root.ids["score_view"].set_scroll_view_scroll_mode(["bars"])


    def check_mode(self, mode: str):
        if self.sidebar_button_current is None:
            ret = None
        else:
            ret = self.sidebar_button_current.name == mode

        self.log_dump(f"Checking mode for {mode} which is {ret}")
        return ret
