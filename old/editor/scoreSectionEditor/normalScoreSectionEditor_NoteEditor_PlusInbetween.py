import time
from typing import Optional

from argumentTrigger import ArgumentTrigger
from editor.scoreSectionEditor.normalScoreSectioneditor import NormalScoreSectionEditor_Editor, AuxiliarySelector
from kivy import Logger
from kivy.clock import Clock
from kivy.graphics import Ellipse, Line, InstructionGroup, Canvas, Translate, PushMatrix, PopMatrix, Color
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from score import fix_and_get_normal_editor_note_ids, Decoration, ScoreSectionStorage
from score.decorations import decorations
from score.notes import notes, Note, dot_radius, dot_spacing, bar_width, flag_length, slanted_flag_length, \
    slanted_flag_height_offset, dot_head_spacing
from selfSizingBoxLayout import SelfSizingBoxLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor_NoteEditor_PlusInbetween.kv")


class Drawer:
    def __init__(self, color, item_translate, item, section_translate):
        self.canvas_container = Canvas()
        self.canvas = Canvas()
        self.canvas_translate = Translate()
        self.canvas_container.add(PushMatrix())
        self.canvas_container.add(self.canvas_translate)
        self.canvas_container.add(color)
        self.canvas_container.add(self.canvas)
        self.canvas_container.add(PopMatrix())

        self.item_translate = item_translate
        self.item = item
        self.section_translate = section_translate

    def add_to(self, canvas):
        canvas.add(self.canvas_container)

    def new_section(self, index):
        canvas = Canvas()
        self.canvas.insert(index, canvas)

    def update(self, index, amount):
        section_before_bar_canvas: Canvas = self.canvas.children[index]
        section_before_bar_canvas.clear()
        section_before_bar_canvas.children.clear()

        if amount == 0:
            section_before_bar_canvas.opacity = 0.3
            section_before_bar_canvas.add(self.item)
            section_before_bar_canvas.add(self.section_translate)
        else:
            section_before_bar_canvas.opacity = 1
            section_before_bar_canvas.add(PushMatrix())
            for i in range(amount):
                section_before_bar_canvas.add(self.item)
                section_before_bar_canvas.add(self.item_translate)
            section_before_bar_canvas.add(PopMatrix())
            section_before_bar_canvas.add(self.section_translate)

    def clear(self):
        self.canvas.clear()

    def remove(self, index):
        self.canvas.remove(self.canvas.children[index])


# noinspection PyPep8Naming
class NormalScoreSectionEditor_NoteEditor_PlusInbetween(NormalScoreSectionEditor_Editor):
    update = None
    update_size = None

    head_translate: Translate
    head_canvas: Canvas
    head_canvas_container: Canvas
    head_canvas_translate: Translate

    note_head_canvases: dict[int, list[Canvas]]  # For opacity
    decoration_colors: list[Color]  # For opacity

    note_objects: dict[int, Note]
    note_object_holder: SelfSizingBoxLayout

    def __init__(self, score_section_instance, **kwargs):
        self.note_head_canvases = {i: [] for i in range(len(notes))}
        self.decoration_colors = []
        self.update = ArgumentTrigger(self._update, -1, True)
        self.update_size = Clock.create_trigger(self._update_size, -1)

        self.head_canvas_container = Canvas()
        self.head_canvas = Canvas()
        self.head_canvas_translate = Translate()
        self.head_canvas_container.add(PushMatrix())
        self.head_canvas_container.add(self.head_canvas_translate)
        self.head_canvas_container.add(self.head_canvas)
        self.head_canvas_container.add(PopMatrix())

        self.section_modifiers_canvas_container = Canvas()
        self.section_modifiers_canvas = Canvas()
        self.section_modifiers_canvas_container.add(PushMatrix())
        self.section_modifiers_canvas_container.add(self.section_modifiers_canvas)
        self.section_modifiers_canvas_container.add(PopMatrix())

        self.section_translate = Translate()
        self.full_bar_line = Line(points=[0, 4/2, 0, 4/2], width=bar_width)
        self.before_bar_line = Line(points=[0, 4/2, flag_length, 4/2], width=bar_width)
        self.after_bar_line = Line(points=[0, 4/2, 0, 4/2], width=bar_width)
        self.slanted_bar_line = Line(points=[0, 0, slanted_flag_length, -slanted_flag_height_offset], width=bar_width)
        self.dot = Ellipse(pos=[0, 0], size=[dot_radius * 2, dot_radius * 2])
        self.full_bar_translate = Translate(0, 2, 0)  # Todo: Actual value
        self.before_bar_translate = Translate(0, 2, 0)  # Todo: Actual value
        self.after_bar_translate = Translate(0, 2, 0)  # Todo: Actual value
        self.slanted_bar_translate = Translate(0, 2, 0)  # Todo: Actual value
        self.dots_translate = Translate(dot_spacing, 0, 0)  # Todo: Actual value
        self.section_modifier = SectionModifier()


        black = Color(rgba=(0, 0, 0, 1))
        self.full_bar_drawer = Drawer(black, self.full_bar_translate, self.full_bar_line, self.section_translate)
        self.before_bar_drawer = Drawer(black, self.before_bar_translate, self.before_bar_line, self.section_translate)
        self.after_bar_drawer = Drawer(black, self.after_bar_translate, self.after_bar_line, self.section_translate)
        self.slanted_bar_drawer = Drawer(black, self.slanted_bar_translate, self.slanted_bar_line, self.section_translate)
        self.dots_drawer = Drawer(black, self.dots_translate, self.dot, self.section_translate)


        self.note_objects = {}
        self.note_object_holder = SelfSizingBoxLayout(anchor="highest", orientation="vertical")
        for (note_id, note_type) in sorted(notes.items(), key=lambda x: x[1]().note_level, reverse=True):
            note: Note = note_type()
            self.note_object_holder.add_widget(note)
            self.note_objects[note_id] = note
            note.opacity = 1

        NormalScoreSectionEditor_Editor.__init__(self, score_section_instance, **kwargs)

        for note in self.score_section_instance.noteHeightCalculator.note_objects.values():
            note.fbind("y", self.update_size)
        self.update_size()

        self.score_section_instance.storage.bind_all(self.update)
        self.score_section_instance.storage.bind(normal_editor_note_ids=lambda _, __: self.update("none"))  # Only need to
                                                                                          # trigger update of note heads
        self.note_object_holder.bind(height=self.update_size)
        self.canvas.add(self.head_canvas_container)
        self.canvas.add(self.section_modifiers_canvas_container)
        self.full_bar_drawer.add_to(self.canvas)
        self.before_bar_drawer.add_to(self.canvas)
        self.after_bar_drawer.add_to(self.canvas)
        self.slanted_bar_drawer.add_to(self.canvas)
        self.dots_drawer.add_to(self.canvas)
        self.update("all")

        self.bottom_note_y_offset = self.section_modifier.height

    def _update_size(self, _):
        full_bar_amount = max(*(section.bars for section in self.score_section_instance.storage), 2)  # Grey bars
        before_bar_amount = max(*(section.before_flags for section in self.score_section_instance.storage), 2)
        after_bar_amount = max(*(section.after_flags for section in self.score_section_instance.storage), 1)

        self.slanted_bar_drawer.canvas_translate.x = self.section_translate.x * len(self.score_section_instance.storage)
        self.width = self.slanted_bar_drawer.canvas_translate.x + slanted_flag_length

        y = self.section_modifier.height
        self.head_canvas_translate.y = y
        y += self.note_object_holder.height + dot_head_spacing
        self.dots_drawer.canvas_translate.y = y
        y += dot_radius * 2
        self.full_bar_drawer.canvas_translate.y = y
        y += full_bar_amount * 2
        self.before_bar_drawer.canvas_translate.y = y
        y += before_bar_amount * 2
        self.after_bar_drawer.canvas_translate.y = y
        self.height = y + max(after_bar_amount, 2) * 2
        y += after_bar_amount * 2
        y -= max((self.score_section_instance.storage[-1].slanted_flags - 1) * 2, 0)
        self.slanted_bar_drawer.canvas_translate.y = y

    def _update(self, changes: list[tuple[tuple[any], dict[str, any]]]):
        Logger.info(f"NSSE_NE_PlusInbetween: Updating {self} with {changes}...")
        t = time.time()

        note_ids = fix_and_get_normal_editor_note_ids(self.score_section_instance.storage)
        width = 0
        note: Note
        for i, note in self.note_objects.items():
            if i in note_ids:
                note.height = note.preferred_height
                note.opacity = 1
                if note.width > width:
                    width = note.width
            else:
                note.height = 0
                note.opacity = 0
        self.section_translate.x = width
        self.full_bar_line.points[2] = width
        self.after_bar_line.points[0] = width - flag_length
        self.after_bar_line.points[2] = width

        # TODO: optimize by skipping stuff that gets overwritten (e.g. add bar before full redraw)
        for change in changes:
            change = change[0]  # We don't care about kwargs
            Logger.debug(f"NSSE_NE_PlusInbetween: Changing {change}")

            if change[0] == "none":  # Probably from need to update something else like note head opacities
                pass

            elif change[0] == "all" or (change[0] == "storage" and change[1] == "set"):
                self.full_redraw()
            elif change[0] == "storage" and change[1] == "insert":
                self.add_section(change[2])
            elif change[0] == "storage" and change[1] == "remove":
                self.remove_section(change[2])

            elif change[0] == "section" and change[1] == "note_ids":
                self.update_head_canvas_colors(self.score_section_instance.storage.index(change[2]))
            elif change[0] == "section" and (change[1] == "bars"):
                self.update_section_full_bars(self.score_section_instance.storage.index(change[2]))
            elif change[0] == "section" and (change[1] == "before_flags"):
                self.update_section_before_bars(self.score_section_instance.storage.index(change[2]))
            elif change[0] == "section" and (change[1] == "after_flags"):
                self.update_section_after_bars(self.score_section_instance.storage.index(change[2]))
            elif change[0] == "section" and (change[1] == "slanted_flags"):
                self.update_section_slanted_bars()
            elif change[0] == "section" and change[1] == "dots":
                self.update_section_dots(self.score_section_instance.storage.index(change[2]))

            elif change[0] == "section" and (change[1] == "decoration_id" or change[1] == "custom_width"):
                pass  # We don't care about these here
            else:
                raise NotImplementedError(f"Score section doesn't know how to change {change}")

        Logger.info(f"NSSE_NE_PlusInbetween: {time.time() - t}s elapsed!")

    def full_redraw(self):
        self.section_modifiers_canvas.clear()
        self.decoration_colors.clear()
        self.head_canvas.clear()
        self.full_bar_drawer.clear()
        self.before_bar_drawer.clear()
        self.after_bar_drawer.clear()
        self.slanted_bar_drawer.clear()
        self.dots_drawer.clear()
        for note_id in self.note_head_canvases:
            self.note_head_canvases[note_id].clear()

        for i in range(len(self.score_section_instance.storage)):
            self.add_section(i)

        self.slanted_bar_drawer.new_section(0)
        self.update_section_slanted_bars()

    def add_section(self, index):
        section_modifier_group = InstructionGroup()
        decoration_color = Color(rgba=(0, 0, 0, 0.1))
        section_modifier_group.add(decoration_color)
        self.decoration_colors.insert(index, decoration_color)
        section_modifier_group.add(self.section_modifier.canvas)
        section_modifier_group.add(self.section_translate)

        self.section_modifiers_canvas.insert(index, section_modifier_group)

        head_group = InstructionGroup()
        for (note_id, note_object) in self.note_objects.items():
            canvas = Canvas()
            self.note_head_canvases[note_id].insert(index, canvas)
            canvas.add(note_object.canvas)
            head_group.add(canvas)
        head_group.add(self.section_translate)
        self.head_canvas.insert(index, head_group)

        self.full_bar_drawer.new_section(index)
        self.before_bar_drawer.new_section(index)
        self.after_bar_drawer.new_section(index)
        self.dots_drawer.new_section(index)

        self.update_head_canvas_colors(index)
        self.update_section_full_bars(index)
        self.update_section_before_bars(index)
        self.update_section_after_bars(index)
        self.update_section_dots(index)

        if index >= len(self.score_section_instance.storage):  # Last item so has slanted bars
            self.update_section_slanted_bars()

    def remove_section(self, index):
        self.section_modifiers_canvas.remove(self.section_modifiers_canvas.children[index])
        self.decoration_colors.pop(index)
        self.head_canvas.remove(self.head_canvas.children[index])
        self.full_bar_drawer.remove(index)
        self.before_bar_drawer.remove(index)
        self.after_bar_drawer.remove(index)
        self.dots_drawer.remove(index)
        for note_id in self.note_head_canvases:
            self.note_head_canvases[note_id].pop(index)

        self.update_size()

        if index >= len(self.score_section_instance.storage):  # Last item so has slanted bars
            self.update_section_slanted_bars()

    def update_head_canvas_colors(self, index):
        for note_id in self.note_head_canvases:
            if note_id in self.score_section_instance.storage[index].note_ids:
                self.note_head_canvases[note_id][index].opacity = 1
            else:
                self.note_head_canvases[note_id][index].opacity = 0.3

    def update_section_full_bars(self, index):
        self.full_bar_drawer.update(index, self.score_section_instance.storage[index].bars)
        self.update_size()

    def update_section_before_bars(self, index):
        self.before_bar_drawer.update(index, self.score_section_instance.storage[index].before_flags)
        self.update_size()

    def update_section_after_bars(self, index):
        self.after_bar_drawer.update(index, self.score_section_instance.storage[index].after_flags)
        self.update_size()

    def update_section_dots(self, index):
        self.dots_drawer.update(index, self.score_section_instance.storage[index].dots)
        self.update_size()

    def update_section_slanted_bars(self):
        self.slanted_bar_drawer.update(0, self.score_section_instance.storage[-1].slanted_flags)
        self.update_size()

    def on_touch_up(self, touch):
        x = touch.pos[0]
        y = touch.pos[1]
        is_add = touch.button == "left"

        if not 0 < x < self.width - slanted_flag_length:
            if x < self.width:  # In slanted bar area
                self.score_section_instance.storage[-1].slanted_flags += 1 if is_add else -1
            return

        if y < 0:
            return
        elif y < self.section_modifier.height:  # Section Modifiers
            index = x // self.section_translate.x
            button = y // 5
            self.handle_section_modifier_button(int(index), button)  # Also does decorations
        elif y < self.dots_drawer.canvas_translate.y:  # Note heads
            index = x // self.section_translate.x
            ry = y - self.section_modifier.height
            self.handle_note_head_buttons(int(index), ry)
        elif y < self.full_bar_drawer.canvas_translate.y:  # Dots
            index = x // self.section_translate.x
            self.score_section_instance.storage[int(index)].dots += 1 if is_add else -1
        elif y < self.before_bar_drawer.canvas_translate.y:  # Full bars
            index = x // self.section_translate.x
            self.score_section_instance.storage[int(index)].bars += 1 if is_add else -1
        elif y < self.after_bar_drawer.canvas_translate.y:  # Before bars
            index = x // self.section_translate.x
            self.score_section_instance.storage[int(index)].before_flags += 1 if is_add else -1
        elif y < self.height:  # After bars
            index = x // self.section_translate.x
            self.score_section_instance.storage[int(index)].after_flags += 1 if is_add else -1
        else:
            return

    def handle_section_modifier_button(self, index, button):
        if button == 0:  # Decorations
            if self.current_decoration_editing_index is not None:
                self.decoration_colors[self.current_decoration_editing_index].rgba = 0, 0, 0, 0.1
            if self.current_decoration_editing_index == index:
                self.current_decoration_editing_index = None
            else:
                self.current_decoration_editing_index = index
                self.decoration_colors[index].rgba = 0, 0, 0, 1
        elif button == 1:  # Remove
            if len(self.score_section_instance.storage) == 1:
                return  # Don't delete last section section
            self.score_section_instance.storage.pop(index)
        else:  # Add
            self.score_section_instance.storage.insert(index + 1, self.score_section_instance.storage[index].copy())

    def handle_note_head_buttons(self, index, ry):
        for nid in sorted(self.note_objects.keys(), key=lambda x: self.note_objects[x].note_level):
            note = self.note_objects[nid]

            if ry < note.height:
                if nid in self.score_section_instance.storage[index].note_ids:
                    self.score_section_instance.storage[index].note_ids.remove(nid)
                else:
                    self.score_section_instance.storage[index].note_ids.append(nid)
                return
            else:
                ry -= note.height



    current_decoration_editing_index: Optional[int] = NumericProperty(allownone=True, defaultvalue=None)

    note_selector: "NoteSelector"
    decoration_selector: "DecorationSelector"
    auxiliary_selector: AuxiliarySelector

    def auxiliary_selector_setup(self, auxiliary_selector: AuxiliarySelector):
        self.auxiliary_selector = auxiliary_selector
        self.note_selector = NoteSelector()
        self.decoration_selector = DecorationSelector()

        self.note_selector.note_editor = self
        self.decoration_selector.note_editor = self
        auxiliary_selector.add_widget(self.note_selector)

        self.bind(current_decoration_editing_index=self.update_auxiliary_selector_contents)

    def _update_auxiliary_selector_contents(self, _):
        self.auxiliary_selector.clear_widgets()

        if self.current_decoration_editing_index is None:
            self.auxiliary_selector.add_widget(self.note_selector)
        else:
            self.auxiliary_selector.add_widget(self.decoration_selector)




class SectionModifier(Widget):
    pass


class Selector(BoxLayout):
    note_editor: "NormalScoreSectionEditor_NoteEditor_PlusInbetween" = ObjectProperty()

    def __init__(self, **kwargs):
        self.do_height = Clock.create_trigger(self._do_height, -1)

        BoxLayout.__init__(self, **kwargs)
        self.do_height()


    def _do_height(self, _):
        self.height = sum(child.height for child in self.children)


class NoteSelector(Selector):
    def on_note_editor(self, _, value):
        for note_id in notes.keys():
            selector = NoteSelectorInside(note_id, value.score_section_instance.storage)
            selector.bind(size=self.do_height)
            self.add_widget(selector)
        self.do_height()


class NoteSelectorInside(RelativeLayout):  # Class that goes inside note selector
    note_id: int
    score_section: ScoreSectionStorage
    note_obj: Note

    def __init__(self, note_id, score_section, **kwargs):
        self.note_id = note_id
        self.score_section = score_section
        self.note_obj = notes[note_id]()

        RelativeLayout.__init__(self, **kwargs)


class DecorationSelector(Selector):
    insides: dict[int, "DecorationSelectorInside"]

    def __init__(self, **kwargs):
        self.insides = {}

        Selector.__init__(self, **kwargs)
        for decoration_id in decorations.keys():
            selector = DecorationSelectorInside(decoration_id, self.on_click)
            selector.bind(size=self.do_height)
            self.add_widget(selector)
            self.insides[decoration_id] = selector

    def on_parent(self, _, __):
        index = self.note_editor.current_decoration_editing_index
        if index is not None:
            did = self.note_editor.score_section_instance.storage[index].decoration_id
            if did is None:
                for inside in self.insides.values():
                    inside.checkbox.active = False
            else:
                self.insides[did].checkbox.active = True

    def on_click(self, decoration_id, state):
        #  If state is true then we set it regardless, if it is false and the ids are equal then set it to none
        if state:
            self.note_editor.score_section_instance.storage[self.note_editor.current_decoration_editing_index].decoration_id = \
                decoration_id
        elif decoration_id == self.note_editor.score_section_instance.storage[self.note_editor.current_decoration_editing_index] \
                .decoration_id:
            self.note_editor.score_section_instance.storage[self.note_editor.current_decoration_editing_index].decoration_id = None


class DecorationSelectorInside(RelativeLayout):
    decoration_id: int
    decoration_obj: Decoration
    click_callback: callable
    container: RelativeLayout = ObjectProperty()
    checkbox: CheckBox = ObjectProperty()

    def __init__(self, decoration_id, click_callback, **kwargs):
        self.decoration_id = decoration_id
        self.decoration_obj = decorations[decoration_id](color=(1, 1, 1, 1))
        self.click_callback = click_callback

        RelativeLayout.__init__(self, **kwargs)

    def on_container(self, _, value):
        value.add_widget(self.decoration_obj)
