import kivy.base
from kivy import metrics
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import ScatterPlane
from kivy.uix.widget import Widget

from renderer.scoreSection.scoreSection_normalDotCreator import ScoreSection_NormalDotCreator

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
g, w, h = ScoreSection_NormalDotCreator((0, 0, 0, 1)).create(7)
print(f"Size: {w, h}")
design_holder.canvas.add(g)
design_holder.canvas.flag_update()
design_holder.size = w, h

root = ScatterPlane(scale=(metrics.mm(1)))
root.pos = 0, 0
root.add_widget(design_holder)

kivy.base.runTouchApp(root)
