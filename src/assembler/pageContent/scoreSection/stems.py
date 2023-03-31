from kivy.clock import Clock
from kivy.graphics import Line, InstructionGroup, Color

from assembler.pageContent.scoreSection import MultiNoteHolder, MultiBarHolder
from score.notes import stem_width, bar_height, Note


def update_line_points(line: Line, note_container: MultiNoteHolder, bar_container: MultiBarHolder):
    if len(note_container.children) > 0:
        bottom_note: Note = min(note_container.children, key=lambda x: x.note_level)
        line.points = \
            note_container.right, \
            bottom_note.y + bottom_note.stem_connection_offset, \
            note_container.right, \
            bar_container.top - bar_height
    else:
        line.points = \
            note_container.right, \
            note_container.y, \
            note_container.right, \
            bar_container.top - bar_height
    line.flag_update()


def draw_stem(note_container: MultiNoteHolder, bar_container: MultiBarHolder):
    ret = InstructionGroup()
    ret.add(Color(rgba=(0, 0, 0, 1)))
    line = Line(width=stem_width)  # We just run updater function
    update_trigger = Clock.create_trigger(
        lambda _: update_line_points(line, note_container, bar_container),
        -1)
    note_container.bind(pos=update_trigger, size=update_trigger)
    bar_container.bind(pos=update_trigger, size=update_trigger)
    update_trigger()
    ret.add(line)
    return ret
