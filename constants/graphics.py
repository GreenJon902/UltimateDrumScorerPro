page_bg_color = [1] * 3

scroll_bar_color = ([0.4] * 3) + [0.8]
scroll_bar_inactive_color = ([0.8] * 3) + [0.2]
scroll_bar_width = "20dp"

sidebar_button_name_to_cursor = {"text": "ibeam", "section": "new_bar", "move": "hand", "note": "arrow"}

minimum_mouse_move_for_score_content_to_not_be_a_click = 5

staff_height = 500
staff_gap = staff_height / 4

note_width = 500
note_color = [0] * 3
temp_note_color = [0, 0.8, 0.8]
temp_note_that_exists_color = [0.7, 0, 0]
note_stem_width = 10
note_stem_height = 600
note_head_width = staff_gap * 1.5
note_flag_dpos = 100, -50
note_flag_gap = 50

note_dot_dpos = note_head_width + 20, -50
note_dot_size = 50, 50

tooltip_bg_color = [0.1] * 3
tooltip_text_color = [1] * 3
tooltip_padding = 5

bar_size = 50
bar_size_hint = None
bar_start_padding = 100

header_color = ([0.5] * 3)
side_bar_color = ([0.4] * 3)
bg_color = ([0.2] * 3)

score_zoom_start = 0.5
score_zoom_min = 0.1
score_zoom_max = 2
score_zoom_step = 0.01

score_zoom_bar_width = 300
score_zoom_bar_size_hint_x = None
score_zoom_sign_color = ([0.2] * 3)

staff_height = 500
staff_gap = staff_height / 4
staff_color = ([0] * 3)
staff_line_width = 5
staff_y_padding = staff_gap

bar_edge_line_width = staff_line_width
bar_edge_repeat_line_width = 30

default_bar_start_line_type = "single"
default_bar_end_line_type = "single"

one_line_text_box_height = 30

add_text_popup_font_size_min_mm = 5
add_text_popup_font_size_max_mm = 50
add_text_popup_font_size_default_mm = 10

mode_button_path = "atlas://resources/atlases/buttons/{name}_button_{state}"

default_none_music_note_width = 0
expanded_none_music_note_width = note_width
none_music_note_expand_time = 0.75
none_music_note_expand_transition = "out_elastic"

section_title_font_size = 200
section_title_height = 200
section_spacer_height = 100
section_height = section_title_height + staff_height + section_spacer_height + (staff_y_padding * 2)
section_title_outline_color = [0] * 3
section_title_outline_width = 10
section_title_padding_x = 100
