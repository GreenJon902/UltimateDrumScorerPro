from app.popups.popup import Popup


class AddTextPopup(Popup):
    def __init__(self, **kwargs):
        text = kwargs.pop("text", None)
        font_size = kwargs.pop("font_size", None)

        Popup.__init__(self, **kwargs)

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
