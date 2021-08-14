from glob import glob

from PIL import Image
from kivy.atlas import Atlas
from kivy.logger import Logger

padding = 5


if __name__ == '__main__':
    Logger.info("AtlasMaker: Creating atlas for buttons")

    button_files = [name for name in glob("../_buttons/*.png")]
    button_files.sort()
    single_size = Image.open(button_files[0]).size
    multiple_size = int((single_size[0] * 3) + (padding * 3)), int((single_size[1] * len(button_files) / 3) + (padding * len(button_files) / 3))

    Atlas.create("buttons", button_files, multiple_size, padding=padding)

    Logger.info("AtlasMaker: Created atlas for buttons")
    Logger.info("AtlasMaker: Creating atlas for notes")

    note_files = [name for name in glob("../_notes/*.png")]
    note_files.sort()
    single_size = Image.open(note_files[0]).size
    multiple_size = int((single_size[0]) + padding), int(
        (single_size[1] * len(note_files)) + (padding * len(note_files)))

    Atlas.create("notes", note_files, multiple_size, padding=padding)

    Logger.info("AtlasMaker: Created atlas for notes")
