from glob import glob

from PIL import Image
from kivy.atlas import Atlas
from kivy.logger import Logger

padding = 5
names_width = {"buttons": 3, "special_notes": 1, "note_heads": 1}

if __name__ == '__main__':
    for name in names_width.keys():
        width = names_width[name]

        Logger.info(f"AtlasMaker: Creating atlas for {name}")

        button_files = [name for name in glob(f"../_{name}/*.png")]
        button_files.sort()
        single_size = Image.open(button_files[0]).size
        multiple_size = int((single_size[0] * width) + (padding * width)), int(
            (single_size[1] * len(button_files) / width) + (padding * len(button_files) / width))

        Atlas.create(f"{name}", button_files, multiple_size, padding=padding)
        Logger.info(f"AtlasMaker: Created atlas for {name}")

