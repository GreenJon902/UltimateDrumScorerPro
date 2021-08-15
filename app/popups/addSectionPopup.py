from app.popups.popup import Popup


class AddSectionPopup(Popup):
    def __init__(self, **kwargs):
        name = kwargs.pop("name", None)

        Popup.__init__(self, **kwargs)

        if name:
            self.ids["name"].text = name

    def get_entered(self):
        array = {"name": self.ids["name"].text}
        self.log_dump(f"Data entered was requested, returning {array}")
        return array

    def on_finish_button(self, _instance, _value):
        data = self.get_entered()


        if data["name"] == "":
            self.log_debug("Finish button clicked but no name entered so ignoring")

        else:
            self.dismiss(correct=True)
            self.log_dump("Finish button clicked, dismissing self")
