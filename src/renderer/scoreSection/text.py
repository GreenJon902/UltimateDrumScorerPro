import kivy.base
from kivy.graphics import PushMatrix, PopMatrix, InstructionGroup, Scale
from kivy.uix.label import Label

l = Label(text="test")
with l.canvas.before:
    PushMatrix()

    Scale(2, 1, 1)
    i = InstructionGroup()

with l.canvas.after:

    PopMatrix()

i.add(PushMatrix())
#i.add(InstructionGroup())
#i.add(PopMatrix())


kivy.base.runTouchApp(l)
