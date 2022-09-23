from app.popups.popup import Popup


class AddSectionPopup(Popup):
    def __init__(self, **kwargs):
        title = kwargs.pop("title", None)

        Popup.__init__(self, **kwargs)

        if title:
            self.ids["title"].text = title

    def get_entered(self):
        array = {"title": self.ids["title"].text}
        self.log_dump(f"Data entered was requested, returning {array}")
        return array

    def on_finish_button(self, _instance, _value):
        data = self.get_entered()


        if data["title"] == "":
            self.log_debug("Finish button clicked but no name entered so ignoring")

        else:
            self.dismiss(correct=True)
            self.log_dump("Finish button clicked, dismissing self")
