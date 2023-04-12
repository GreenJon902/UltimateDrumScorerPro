from kivy.clock import Clock
from kivy.core.window import Window
from kivy.input import MotionEvent
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout

from assembler.pageContent.scoreSection import ScoreSection
from editor.scoreSectionEditor.normalScoreSectioneditor import NormalScoreSectionEditor_NoteEditor
from score import ScoreSectionSectionStorage, fix_and_get_normal_editor_note_ids
from score.notes import notes, Note
from selfSizingBoxLayout import SelfSizingBoxLayout

Builder.load_file("editor/scoreSectionEditor/normalScoreSectionEditor_NoteEditor_PlusInbetween.kv")


# noinspection PyPep8Naming
class NormalScoreSectionEditor_NoteEditor_PlusInbetween(NormalScoreSectionEditor_NoteEditor):
    full_redraw = None

    note_holder: SelfSizingBoxLayout = ObjectProperty()
    plus_holder: SelfSizingBoxLayout = ObjectProperty()
    cross_holder: SelfSizingBoxLayout = ObjectProperty()

    score_section_instance: ScoreSection

    def __init__(self, score_section_instance, **kwargs):
        self.score_section_instance = score_section_instance
        self.full_redraw = Clock.create_trigger(self._full_redraw, -1)
        NormalScoreSectionEditor_NoteEditor.__init__(self, **kwargs)

        self.full_redraw()

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

    def insert_new_section_section(self, i):
        self.score_section_instance.score.insert(i, ScoreSectionSectionStorage(note_ids=[]))
        self.full_redraw()

    def remove_section_section(self, i):
        self.score_section_instance.score.pop(i)
        self.full_redraw()


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
