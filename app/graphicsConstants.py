page_bg_color = [1] * 3
page_size = 2000, 3000
page_with_to_height_ratio = page_size[1] / page_size[0]  # which is also √2
page_size_mm = 200, 300
page_pixels_in_mm = 10


def mm_to_font_size_func(mm):
    return (mm / 25.4) / 72


scroll_bar_color = ([0.4] * 3) + [0.8]
scroll_bar_inactive_color = ([0.8] * 3) + [0.2]
scroll_bar_width = "20dp"

sidebar_button_name_to_cursor = {"add_text": "ibeam", "add_bar": "new_bar", "None": "arrow"}
