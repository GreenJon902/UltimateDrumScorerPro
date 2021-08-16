from kivy.atlas import Atlas
from kivy.graphics import Canvas, Rectangle

from app.graphicsConstants import note_width

image_textures = Atlas("resources/atlases/notes.atlas").textures


class Note:
    length: int
    name: str

    def __init__(self, length=1, name="rest"):
        self.name = name
        self.length = length

        self.canvas = Canvas()

        if self.name in image_textures.keys():
            rect = Rectangle(pos=(0, 0),
                             size=(note_width,
                                   (image_textures[self.name].width / image_textures[self.name].height) * note_width),
                             texture=image_textures[self.name])
            self.canvas.add(rect)
