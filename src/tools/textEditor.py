import kivy.base

from editor.textEditor import TextEditor
from scoreStorage.textStorage import TextStorage

storage = TextStorage()

te = TextEditor(storage)

kivy.base.runTouchApp(te)
