from kivy.app import App
from kivy.uix.popup import Popup

from logger.classWithLogger import ClassWithLogger


class MyPopup(Popup, ClassWithLogger):
    def __init__(self, **kwargs):
        Popup.__init__(self, **kwargs)
        ClassWithLogger.__init__(self)

        self.register_event_type("on_cancelled")
        self.register_event_type("on_submitted")

    def get_entered(self):
        raise NotImplementedError("No get_entered method implemented")

    def on_finish_button(self, _instance, _value):
        pass


    def dismiss(self, *args, correct=False, **kwargs):  # If correct is false then that means it was auto_dismissed
        if correct:
            self.dispatch("on_submitted", self.get_entered())

        else:
            self.dispatch("on_cancelled")

        Popup.dismiss(self, *args, **kwargs)

    def on_cancelled(self):
        pass

    def on_submitted(self, data):
        pass



class AddTextPopup(MyPopup):
    def __init__(self, **kwargs):
        text = kwargs.pop("text", None)
        font_size = kwargs.pop("font_size", None)

        MyPopup.__init__(self, **kwargs)

        if text:
            self.ids["text"].text = text
        if font_size:
            self.ids["font_size"].value = font_size


    def get_entered(self):
        array = {"text": self.ids["text"].text, "font_size": self.ids["font_size"].value}
        self.log_dump(f"Data entered was requested, returning {array}")
        return array


    def on_finish_button(self, _instance, _value):
        data = self.get_entered()

        if data["text"] == "":
            self.log_debug("Finish button clicked but no text entered so ignoring")

        else:
            self.dismiss(correct=True)
            self.log_dump("Finish button clicked, dismissing self")



class AddSectionPopup(MyPopup):
    def __init__(self, **kwargs):
        name = kwargs.pop("name", None)

        MyPopup.__init__(self, **kwargs)

        if name:
            self.ids["name"].text = name

    def get_entered(self):
        pass
