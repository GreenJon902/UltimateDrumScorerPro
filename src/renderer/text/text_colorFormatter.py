import re

from renderer.text.text_formatterBase import Text_FormatterBase


class Text_ColorFormatter(Text_FormatterBase):
    """
    Takes hex codes and converts them to the kivy color format.
    Formats:
    - &#000 - RGB
    - &#0000 - RGBA
    - &#000000 - RRGGBB
    - &#00000000 - RRGGBBAA
    """

    color_regex = re.compile(r"&#([\dabcdef]{3}(?:[\dabcdef]{1})?(?:[\dabcdef]{2})?(?:[\dabcdef]{2})?)(.*)")
    color_substitution = r"[color=#\g<1>]\g<2>[/color]"

    def format(self, text) -> str:
        text = self.color_regex.sub(self.color_substitution, text)
        return text


__all__ = ["Text_ColorFormatter"]
