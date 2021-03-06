from kivy.clock import Clock
from kivy.input import MotionEvent

import constants
from app.uix.scoreContent import ScoreContent


class ScoreContentWithPopup(ScoreContent):
    is_active = False  # For cancel - true if has been submitted at least once

    def on_touch_up(self, touch: MotionEvent):
        s = constants.graphics.minimum_mouse_move_for_score_content_to_not_be_a_click

        if touch.uid == self.click_current_uid:
            if ((s * -1) <= touch.dx <= s) and ((s * -1) <= touch.dy <= s):

                # Get start pos since shouldn't have moved---
                x, y = touch.pos
                ox, oy = touch.opos

                tdx = ox - x
                tdy = oy - y

                self.x += tdx
                self.y += tdy
                # -------------------------------------------

                self.open_popup_with_pre_values()

            self.click_current_uid = None
            return True

        return False


    def __init__(self, **kwargs):
        no_popup = kwargs.pop("no_popup", False)

        ScoreContent.__init__(self, **kwargs)

        if no_popup:
            Clock.schedule_once(lambda _elapsed_time: self.popup_submitted(self, {}), -1)

        else:
            self.popup()

    def popup(self, **kwargs):
        self.log_debug("Creating popup to edit text")
        popup = self.get_popup_class(**kwargs)
        popup.bind(on_submitted=self.popup_submitted, on_cancelled=self.popup_cancelled)
        popup.open()

    def _popup_submitted(self, instance, data):
        self.log_dump(f"Popup submitted, data - {data}")
        self.popup_submitted(instance, data)


    def popup_cancelled(self, _instance):
        if not self.is_active:
            self.log_dump("Popup cancelled but was already text so not removing")

            self.parent.remove_widget(self)

        else:
            self.log_dump("Popup cancelled")



    def get_popup_class(self, **kwargs):
        raise NotImplementedError("No get_popup_class method implemented")


    def popup_submitted(self, instance, data):
        raise NotImplementedError("No popup_submitted method implemented")


    def open_popup_with_pre_values(self):
        raise NotImplementedError("No popup_with_pre_values method implemented")