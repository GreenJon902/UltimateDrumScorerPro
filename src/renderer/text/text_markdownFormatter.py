import re

from renderer.text.text_formatterBase import Text_FormatterBase


class Text_MarkdownFormatter(Text_FormatterBase):
    """
    A basic Markdown implementation, it converts it to the kivy markup format.
    Features Implemented:
    - \*\***Bold**\*\*
    - \__Italics_\_
    - \**Italics*\*
    - \_\_<u>Underline</u>\_\_
    - \~\~~~strikethrough~~\~\~
    """

    bold_regex = re.compile(r"\*\*(.+?)\*\*")
    bold_substitution = r"[b]\g<1>[/b]"
    underline_regex = re.compile(r"__(.+?)__")
    underline_substitution = r"[u]\g<1>[/u]"
    italic_regex = re.compile(r"\*(.+?)\*")
    italic2_regex = re.compile(r"_(.+?)_")
    italic_substitution = r"[i]\g<1>[/i]"
    strikethrough_regex = re.compile(r"~~(.+?)~~")
    strikethrough_substitution = r"[s]\g<1>[/s]"

    def format(self, text) -> str:
        text = self.bold_regex.sub(self.bold_substitution, text)
        text = self.underline_regex.sub(self.underline_substitution, text)
        text = self.italic_regex.sub(self.italic_substitution, text)
        text = self.italic2_regex.sub(self.italic_substitution, text)
        text = self.strikethrough_regex.sub(self.strikethrough_substitution, text)
        return text


__all__ = ["Text_MarkdownFormatter"]
