# Usage
TextRenderer will draw text to a page and supports formatting.
It can take any amount of formatters which are ordered. It can also take a renderer which will do the drawing of the text.

# Component APIs
- Formatters
  - .format(text) -> str - Modifies the input string with a set of internal rules.  
<br>
  - ColorFormatter - Takes hex codes and converts them to the kivy color format.  
    Formats:
    - &#000 - RGB
    - &#0000 - RGBA
    - &#000000 - RRGGBB
    - &#00000000 - RRGGBBAA
  - MarkdownFormatter - A basic Markdown implementation, it converts it to the kivy markup format.  
    Features Implemented:
    - \*\***Bold**\*\*
    - \__Italics_\_
    - \**Italics*\*
    - \_\_<u>Underline</u>\_\_
    - \~\~~~strikethrough~~\~\~  
<br>
- Renderers
  - .update(text, do_formatting, font_size) - Renders text with the font size, do formatting tells it whether to use kivy markup or not.  
<br>
  - NormalRenderer - What I said above.
  - CorrectlySizedRenderer - Renders it as specified above, but also accounts for any scaling that may make the text render at too low a resolution.
    - Takes an argument of the widget where it is rendered so it can calculate the current scaling at that point.