import time

from kivy import Logger
from kivy.properties import ListProperty, ObjectProperty

from renderer import Renderer
from renderer.text.text_formatterBase import Text_FormatterBase
from renderer.text.text_rendererBase import Text_RendererBase
from scoreStorage.textStorage import TextStorage


class TextRenderer(Renderer):
    storage: TextStorage

    renderer: Text_RendererBase = ObjectProperty(allownone=True)

    formatters: list[Text_FormatterBase] = ListProperty()
    _formatted_text: str

    def __init__(self, *args, **kwargs):
        Renderer.__init__(self, *args, **kwargs)
        self.bind(formatters=lambda _, __: self.dispatch_instruction("reformat"),
                  renderer=lambda _, __: self.dispatch_instruction("render"))
        self.dispatch_instruction("all")

    def process_instructions(self, instructions: list[tuple[tuple[any, ...], dict[str, any]]]):
        Logger.info(f"TextRenderer: Updating {self} with {instructions}...")
        t = time.time()
        commands = instructions[:][0][0]

        fallthrough = False
        if "all" in commands:  # Imagine a switch statement but unlike python, THIS ONE HAS FALL THROUGH
            fallthrough = True
        if fallthrough or "reformat" in commands:
            Logger.debug(f"TextRenderer: Reformatting...")
            self.reformat()
            fallthrough = True
        if fallthrough or "render" in commands:
            Logger.debug(f"TextRenderer: Rendering...")
            if self.renderer is not None:
                self.renderer.update(self._formatted_text, self.storage.do_formatting, self.storage.font_size)
                self.size = self.renderer.size
                self.canvas.clear()
                self.canvas.add(self.renderer.canvas)
            else:
                Logger.warning("TextRenderer: No renderer supplied")  # Warn as this doesn't make sense not to have

        Logger.info(f"TextRenderer: {time.time() - t}s elapsed!")



    def set_storage(self, storage):
        if self.storage is not None:
            self.storage.unbind(text=self.on_text, font_size=self.on_font_size, do_formatting=self.on_do_formatting)
        Renderer.set_storage(self, storage)
        self.storage.bind(text=self.on_text, font_size=self.on_font_size, do_formatting=self.on_do_formatting)
        self.dispatch_instruction("all")
    def on_text(self, _, value):
        self.dispatch_instruction("reformat")
    def on_do_formatting(self, _, value):
        self.dispatch_instruction("reformat")
    def on_font_size(self, _, value):
        self.dispatch_instruction("render")

    def reformat(self):
        text = self.storage.text
        if self.storage.do_formatting:
            for formatter in self.formatters:
                text = formatter.format(text)
        self._formatted_text = text


__all__ = ["TextRenderer"]
