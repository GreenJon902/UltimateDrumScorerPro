from kivy.app import App
from kivy.uix.popup import Popup as KvPopup

from app.globalBindings import GlobalBindings
from logger import ClassWithLogger


class Popup(KvPopup, ClassWithLogger):
    cursor_before: str

    def __init__(self, **kwargs):
        KvPopup.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.register_event_type("on_cancelled")
        self.register_event_type("on_submitted")

    def get_entered(self):
        raise NotImplementedError("No get_entered method implemented")

    def on_finish_button(self, _instance, _value):
        pass


    def open(self, *args, **kwargs):
        KvPopup.open(self, *args, **kwargs)

        self.cursor_before = App.get_running_app().current_cursor
        GlobalBindings.dispatch("set_cursor", "arrow")


    def dismiss(self, *args, correct=False, **kwargs):  # If correct is false then that means it was auto_dismissed
        if correct:
            self.dispatch("on_submitted", self.get_entered())

        else:
            self.dispatch("on_cancelled")

        KvPopup.dismiss(self, *args, **kwargs)
        GlobalBindings.dispatch("set_cursor", self.cursor_before)
        del self.cursor_before

    def on_cancelled(self):
        pass

    def on_submitted(self, data):
        pass
