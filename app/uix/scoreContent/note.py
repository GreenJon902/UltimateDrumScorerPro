from kivy.atlas import Atlas
from kivy.graphics import Canvas, Rectangle, Ellipse, Color, Line

from app.graphicsConstants import note_width, staff_height, staff_gap, note_tail_width, note_foot_width

image_textures = Atlas("resources/atlases/notes.atlas").textures


class Note:
    length: int
    name: str

    def __init__(self, length=1, name="rest"):
        self.name = name
        self.length = length

        self.canvas = Canvas()
        self.canvas.add(Color(rgb=(0, 0, 0)))

        if self.name in image_textures.keys():
            rect = Rectangle(pos=(0, 0),
                             size=(note_width, staff_height),
                             texture=image_textures[self.name])
            self.canvas.add(rect)

        else:
            if self.name == "bass":  # TODO: Find a better way of doing this
                foot = Ellipse(pos=(0, staff_gap * 0),
                               size=(note_foot_width, staff_gap))

                tail = Line(points=(note_foot_width - note_tail_width, staff_gap * 0.5,
                                    note_foot_width - note_tail_width, ((staff_gap * 0.5) + staff_height)),
                            width=note_tail_width)

                self.canvas.add(foot)
                self.canvas.add(tail)


            elif self.name == "snare":
                foot = Ellipse(pos=(0, staff_gap * 2),
                               size=(note_foot_width, staff_gap))

                tail = Line(points=(note_foot_width - note_tail_width, staff_gap * 2.5,
                                    note_foot_width - note_tail_width, ((staff_gap * 2.5) + staff_height)),
                            width=note_tail_width)

                self.canvas.add(foot)
                self.canvas.add(tail)


