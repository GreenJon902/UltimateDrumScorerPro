import kivy.base
from kivy import metrics
from kivy.lang import Builder
from kivy.metrics import mm
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.widget import Widget

from scoreSectionDesigns.notes import notes, check_notes

check_notes()
design = notes[0]



Builder.load_string("""
<ScatterPlane>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: -2, -2
            size: self.width + 4, self.height + 4
""")


class MyBoxLayout(BoxLayout):  # Allow no touch events through
    def on_touch_down(self, touch):
        pass
    def on_touch_move(self, touch):
        pass
    def on_touch_up(self, touch):
        pass



design_holder = Widget(size_hint=(None, None))
with design_holder.canvas:
    design.draw()

root = ScatterPlane(scale=(metrics.mm(10) / 10), size=(mm(10), mm(10)), size_hint=(None, None))
root.set_center_x(100)
root.set_center_y(100)
root.add_widget(design_holder)

kivy.base.runTouchApp(root)
