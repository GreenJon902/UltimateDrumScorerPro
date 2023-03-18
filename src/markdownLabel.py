import re

from kivy.core.text.markup import MarkupLabel as CoreMarkupLabel
from kivy.uix.label import Label
from kivy.utils import get_hex_from_color


class CoreMarkdownLabel(CoreMarkupLabel):
    bold_regex = re.compile(r"\*\*(.+?)\*\*")
    bold_substitution = r"[b]\g<1>[/b]"
    underline_regex = re.compile(r"__(.+?)__")
    underline_substitution = r"[u]\g<1>[/u]"
    italic_regex = re.compile(r"\*(.+?)\*")
    italic2_regex = re.compile(r"_(.+?)_")
    italic_substitution = r"[i]\g<1>[/i]"
    color_regex = re.compile(r"&#([\dabcdef]{3}(?:[\dabcdef]{1})?(?:[\dabcdef]{2})?(?:[\dabcdef]{2})?)(.*)")
    color_substitution = r"[color=#\g<1>]\g<2>[/color]"

    splitter_regex = re.compile(r"(\[.*?])")

    @property
    def markup(self):
        text = self.label

        text = self.bold_regex.sub(self.bold_substitution, text)
        text = self.underline_regex.sub(self.underline_substitution, text)
        text = self.italic_regex.sub(self.italic_substitution, text)
        text = self.italic2_regex.sub(self.italic_substitution, text)
        text = self.color_regex.sub(self.color_substitution, text)

        # Markdown has been converted to the kivy format, now we just have use the standard behavior that kivy uses
        s = re.split(self.splitter_regex, text)
        s = [x for x in s if x != '']
        return s


class MarkdownLabel(Label):
    def _create_label(self):  # Modified version of original to use only CoreMarkdownLabel
        dkw = {x: getattr(self, x) for x in self._font_properties}
        dkw['usersize'] = self.text_size
        if self.disabled:
            dkw['color'] = self.disabled_color
            dkw['outline_color'] = self.disabled_outline_color
        self._label = CoreMarkdownLabel(**dkw)

    def texture_update(self, *largs):  # Modified version of original to use only CoreMarkdownLabel
        '''Force texture recreation with the current Label properties.

        After this function call, the :attr:`texture` and :attr:`texture_size`
        will be updated in this order.
        '''
        self.texture = None

        if (not self._label.text or
                (self.halign == 'justify' or self.strip) and
                not self._label.text.strip()):
            self.texture_size = (0, 0)
            self.is_shortened = False

            self.refs, self._label._refs = {}, {}
            self.anchors, self._label._anchors = {}, {}
        else:
            text = self.text
            # we must strip here, otherwise, if the last line is empty,
            # markup will retain the last empty line since it only strips
            # line by line within markup
            if self.halign == 'justify' or self.strip:
                text = text.strip()
            self._label.text = ''.join(('[color=',
                                        get_hex_from_color(
                                            self.disabled_color if
                                            self.disabled else self.color),
                                        ']', text, '[/color]'))
            self._label.refresh()
            # force the rendering to get the references
            if self._label.texture:
                self._label.texture.bind()
            self.refs = self._label.refs
            self.anchors = self._label.anchors

            texture = self._label.texture
            if texture is not None:
                self.texture = self._label.texture
                self.texture_size = list(self.texture.size)
            self.is_shortened = self._label.is_shortened
