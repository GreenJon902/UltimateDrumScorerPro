import time

from kivy import Logger
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Ellipse, Color, Line, InstructionGroup, Canvas, Translate, PushMatrix, PopMatrix
from kivy.input import MotionEvent
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, OptionProperty
from kivy.uix.relativelayout import RelativeLayout

from argumentTrigger import ArgumentTrigger
from assembler.pageContent.scoreSection import ScoreSection
from betterSizedLabel import BetterSizedLabel
from editor.scoreSectionEditor.normalScoreSectioneditor import NormalScoreSectionEditor_NoteEditor
from score import ScoreSectionSectionStorage
from score.notes import notes, Note, dot_radius, dot_spacing, bar_width
from selfSizingBoxLayout import SelfSizingBoxLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor_NoteEditor_PlusInbetween.kv")


# noinspection PyPep8Naming
class NormalScoreSectionEditor_NoteEditor_PlusInbetween(NormalScoreSectionEditor_NoteEditor):
    update = None
    update_size = None

    head_translate: Translate
    head_canvas: Canvas
    head_canvas_container: Canvas
    head_canvas_translate: Translate

    score_section_instance: ScoreSection
    note_head_canvases: dict[int, list[Canvas]]  # For opacity

    note_objects: dict[int, Note]
    note_object_holder: SelfSizingBoxLayout

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        self.note_head_canvases = {i: [] for i in range(len(notes))}
        self.note_holder_canvas = Canvas()
        self.update = ArgumentTrigger(self._update, -1, True)
        self.update_size = Clock.create_trigger(self._update_size, -1)

        self.head_translate = Translate()
        self.head_canvas_container = Canvas()
        self.head_canvas = Canvas()
        self.head_canvas_translate = Translate()
        self.head_canvas_container.add(PushMatrix())
        self.head_canvas_container.add(self.head_canvas_translate)
        self.head_canvas_container.add(self.head_canvas)
        self.head_canvas_container.add(PopMatrix())

        self.note_objects = {}
        self.note_object_holder = SelfSizingBoxLayout(anchor="highest", orientation="vertical")
        self.note_object_holder.bind(width=lambda _, value: (setattr(self.head_canvas_translate, "x",
                                                                     value)))
        for (note_id, note_type) in notes.items():
            note: Note = note_type()
            self.note_object_holder.add_widget(note)
            self.note_objects[note_id] = note
            note.opacity = 1

        NormalScoreSectionEditor_NoteEditor.__init__(self, **kwargs)

        for note in self.score_section_instance.noteHeightCalculator.note_objects.values():
            note.fbind("y", self.update_size)
        self.update_size()

        self.score_section_instance.score.bind_all(self.update)
        self.canvas.add(self.head_canvas_container)
        self.update("all")

    def _update_size(self, _):
        pass

    def _update(self, changes: list[tuple[tuple[any], dict[str, any]]]):
        Logger.info(f"NSSE_NE_PlusInbetween: Updating {self} with {changes}...")
        t = time.time()

        used_note_ids = {note_id for section in self.score_section_instance.score for note_id in section.note_ids}
        width = 0
        note: Note
        for i, note in self.note_objects.items():
            if i in used_note_ids:
                note.height = note.preferred_height
                note.opacity = 1
                if note.width > width:
                    width = note.width
            else:
                note.height = 0
                note.opacity = 0
        self.head_translate.x = width

        # TODO: optimize by skipping stuff that gets overwritten (e.g. add bar before full redraw)
        for change in changes:
            change = change[0]  # We don't care about kwargs
            Logger.debug(f"NSSE_NE_PlusInbetween: Changing {change}")

            if change[0] == "all" or (change[0] == "storage" and change[1] == "set"):
                self.full_redraw()
            elif change[0] == "storage" and change[1] == "insert":
                self.add_section(change[2])
                pass
            #elif change[0] == "storage" and change[1] == "remove":
            #    self.remove_section(change[2])
            #    pass

            #elif change[0] == "section" and change[1] == "note_ids":
            #    self.update_section_notes(self.score.index(change[2]))
            #    pass
            #elif change[0] == "section" and (change[1] == "bars" or change[1] == "before_flags" or change[1] ==
            #                                 "after_flags" or change[1] == "slanted_flags"):
            #    self.update_section_bars(self.score.index(change[2]))
            #    pass
            #elif change[0] == "section" and change[1] == "dots":
            #    self.update_section_dots(self.score.index(change[2]))
            #    pass
            else:
                raise NotImplementedError(f"Score section doesn't know how to change {change}")

        Logger.info(f"NSSE_NE_PlusInbetween: {time.time() - t}s elapsed!")

    def full_redraw(self):
        self.note_holder_canvas.clear()

        for i in range(len(self.score_section_instance.score)):
            self.add_section(i)

    def add_section(self, index):
        group = InstructionGroup()
        for (note_id, note_object) in self.note_objects.items():
            canvas = Canvas()
            self.note_head_canvases[note_id].insert(index, canvas)
            canvas.add(note_object.canvas)
            group.add(canvas)
        group.add(self.head_translate)

        self.head_canvas.insert(index, group)
        self.update_head_canvas_colors(index)

    def update_head_canvas_colors(self, index):
        for note_id in self.note_head_canvases:
            if note_id in self.score_section_instance.score[index].note_ids:
                self.note_head_canvases[note_id][index].opacity = 1
            else:
                self.note_head_canvases[note_id][index].opacity = 0.3




    """
    def _full_redraw(self, _):
        # Notes --------------------------------------------------------------------------------------------------------
        note_ids = fix_and_get_normal_editor_note_ids(self.score_section_instance.score)
        ordered_note_types = sorted([(note_id, notes[note_id]) for note_id in note_ids],
                                    key=lambda x: x[1]().note_level,
                                    reverse=True)  # Reverse cause of how they get added

        self.note_holder.clear_widgets()
        for i in range(len(self.score_section_instance.score)):
            section = self.score_section_instance.score[i]
            holder = SelfSizingBoxLayout(orientation="vertical")
            for (note_id, note_type) in ordered_note_types:
                note: Note = note_type()
                note.color[3] = 1 if note_id in section.note_ids else 0.1
                note.bind(on_touch_down=lambda _, touch, note_=note, section_=section, note_id_=note_id:
                          note_clicked(note_, touch, section_, note_id_))
                holder.add_widget(note)
            self.note_holder.add_widget(holder, index=len(self.note_holder.children))

        # New SectionSection buttons -----------------------------------------------------------------------------------
        self.plus_holder.clear_widgets()
        for i in reversed(range(len(self.score_section_instance.score) + 1)):
            if i != len(self.score_section_instance.score):  # Not last one
                note_holder = self.note_holder.children[i - 1]
                plus = Plus(width=note_holder.width)
                note_holder.bind(width=lambda _, value, _plus=plus: setattr(_plus, "width", value))
            else:
                first_note_holder = self.note_holder.children[0]
                plus = Plus(custom_click_width=first_note_holder.width)
                plus.width = plus.default_width
                first_note_holder.bind(width=lambda _, value, _plus=plus: setattr(_plus, "custom_click_width", value))
            plus.bind(on_touch_down=lambda _, touch, _plus=plus, _i=i:
                      hover_button_clicked(_plus, touch, lambda: self.insert_new_section_section(_i)))
            self.plus_holder.add_widget(plus)

        self.cross_holder.clear_widgets()
        for i in reversed(range(len(self.score_section_instance.score))):
            note_holder = self.note_holder.children[i - 1]
            cross = Cross(width=note_holder.width)
            note_holder.bind(width=lambda _, value, _cross=cross: setattr(_cross, "width", value))
            cross.bind(on_touch_down=lambda _, touch, _cross=cross, _i=i:
                       hover_button_clicked(_cross, touch, lambda: self.remove_section_section(_i)))
            self.cross_holder.add_widget(cross)

        self.bottom_note_y_offset = self.plus_holder.children[0].height + self.cross_holder.children[0].height

        # Bar & Dot buttons --------------------------------------------------------------------------------------------
        self.bar_holder.clear_widgets()
        for i in range(len(self.score_section_instance.score)):
            note_holder = self.note_holder.children[i]
            bar_configurer = BarConfigurer(self, width=note_holder.width,
                                           before_bars=self.score_section_instance.score[i].before_flags,
                                           after_bars=self.score_section_instance.score[i].after_flags,
                                           bars=self.score_section_instance.score[i].bars)
            note_holder.bind(width=lambda _, value, _bar_configurer=bar_configurer:
                             setattr(_bar_configurer, "width", value))
            self.bar_holder.add_widget(bar_configurer)

    def insert_new_section_section(self, i):
        self.score_section_instance.score.insert(i, ScoreSectionSectionStorage(note_ids=[]))
        self.full_redraw()  # TODO: Make this more efficient

    def remove_section_section(self, i):
        self.score_section_instance.score.pop(i)
        self.full_redraw()  # TODO: Make this more efficient

    def bar_configure(self, bar_configurer, place, is_add):  # Does dots too
        index = self.bar_holder.children.index(bar_configurer)
        d = is_add * 2 - 1
        if place == "dots":
            self.score_section_instance.score[index].dots += d
            self.bar_holder.children[index].dots = self.score_section_instance.score[index].dots
        elif place == "before":
            self.score_section_instance.score[index].before_flags += d
            self.bar_holder.children[index].before_bars = self.score_section_instance.score[index].before_flags
        elif place == "after":
            self.score_section_instance.score[index].after_flags += d
            self.bar_holder.children[index].after_bars = self.score_section_instance.score[index].after_flags
        elif place == "full":
            self.score_section_instance.score[index].bars += d
            self.bar_holder.children[index].bars = self.score_section_instance.score[index].bars"""


def note_clicked(note: Note, touch: MotionEvent, section: ScoreSectionSectionStorage, note_id: int):
    if note.collide_point(*touch.pos):
        if note_id in section.note_ids:
            section.note_ids.remove(note_id)
        else:
            section.note_ids.append(note_id)

        note.color[3] = 1 if note_id in section.note_ids else 0.1
        return True


class HoverButton(RelativeLayout):
    mouse_over = BooleanProperty(defaultvalue=False)
    custom_click_width = NumericProperty(defaultvalue=None, allownone=True)  # Width which is checked for mouse, None
                                                                             # for inherit from widget

    def __init__(self, **kwargs):
        RelativeLayout.__init__(self, **kwargs)
        Window.bind(mouse_pos=self.mouse_move)

    def mouse_move(self, _, pos):
        pos = self.to_widget(*pos, relative=True)
        if self.collide_point(*pos):
            self.mouse_over = True
        else:
            self.mouse_over = False


def hover_button_clicked(button: HoverButton, touch: MotionEvent,
                         callback: callable):
    pos = button.to_local(*touch.pos)
    if button.collide_point(*pos):
        callback()
        return True


class Plus(HoverButton):
    default_width: int = NumericProperty(defaultvalue=None)

    def collide_point(self, x, y):
        hw = (self.width if self.custom_click_width is None else self.custom_click_width) / 2
        if -hw < x < hw and 0 < y < self.height:
            return True
        return False


class Cross(HoverButton):
    def collide_point(self, x, y):
        if 0 < x < self.width and 0 < y < self.height:
            return True
        return False


class BarConfigurer(RelativeLayout):  # Also handles flags and dots
    dots_label: BetterSizedLabel = ObjectProperty()
    before_bar_label: BetterSizedLabel = ObjectProperty()
    after_bar_label: BetterSizedLabel = ObjectProperty()
    full_bar_label: BetterSizedLabel = ObjectProperty()
    dots: int = NumericProperty(0)
    before_bars: int = NumericProperty(0)
    after_bars: int = NumericProperty(0)
    bars: int = NumericProperty(0)

    editor: NormalScoreSectionEditor_NoteEditor_PlusInbetween

    def __init__(self, editor, **kwargs):
        self.editor = editor
        RelativeLayout.__init__(self, **kwargs)

    def on_touch_up(self, touch: MotionEvent):
        x = touch.x - self.x
        y = touch.y - self.y
        is_add = touch.button == "left"
        if 0 < x < self.width:
            if self.dots_label.y < y < self.dots_label.top:
                self.editor.bar_configure(self, "dots", is_add)
            elif self.before_bar_label.y < y < self.before_bar_label.top:
                self.editor.bar_configure(self, "before", is_add)
            elif self.after_bar_label.y < y < self.after_bar_label.top:
                self.editor.bar_configure(self, "after", is_add)
            elif self.full_bar_label.y < y < self.full_bar_label.top:
                self.editor.bar_configure(self, "full", is_add)


class BarButton(RelativeLayout):  # And dots and flags
    amount: int = NumericProperty()
    type: str = OptionProperty("bars", options=("bars", "before_bars", "after_bars", "dots"))
    update = None

    def __init__(self, **kwargs):
        self.update = Clock.create_trigger(self._update, -1)
        RelativeLayout.__init__(self, **kwargs)
        self.bind(amount=self.update)
        self.update()

    def _update(self, _):
        self.canvas.clear()

        if self.amount == 0:
            self.canvas.add(Color(rgba=(0, 0, 0, 0.5)))
            self.canvas.add(self.make_instruction(0, 4 / 2))
            self.height = 4
        else:
            self.canvas.add(Color(rgba=(0, 0, 0, 1)))
            x = 0
            y = 0
            for i in range(self.amount):
                self.canvas.add(self.make_instruction(x, y + 4 / 2))
                if self.type == "dots":
                    x += dot_spacing
                else:
                    y += 2  # Todo: get proper value
            self.height = max(4, y)

    def make_instruction(self, x=0, y: float=0):
        if self.type == "bars":
            line = Line(points=[x, y, x + self.width, y], width=bar_width)
            self.bind(width=lambda *args, self_=self: setattr(line, "points", [x, y, x + self_.width, y]))
            return line
        elif self.type == "before_bars":
            line = Line(points=[x, y, x + self.width / 2, y], width=bar_width)
            self.bind(width=lambda *args, self_=self: setattr(line, "points", [x, y, x + self.width / 2, y]))
            return line
        elif self.type == "after_bars":
            line = Line(points=[x + self.width / 2, y, x + self.width, y], width=bar_width)
            self.bind(width=lambda *args, self_=self: setattr(line, "points", [x + self.width / 2, y, x + self.width, y]))
            return line
        elif self.type == "dots":
            return Ellipse(pos=[x, y - dot_radius], size=[dot_radius * 2, dot_radius * 2])