from glob import glob

from PIL import Image
from kivy.atlas import Atlas

padding = 2


if __name__ == '__main__':
    button_files = [name for name in glob("../_buttons/*.png")]
    single_size = Image.open(button_files[0]).size
    multiple_size = int((single_size[0] * 3) + (padding * 3)), int((single_size[1] * len(button_files) / 3) + (padding * len(button_files) / 3))

    atlas = Atlas.create("buttons", button_files, multiple_size, padding=padding)
