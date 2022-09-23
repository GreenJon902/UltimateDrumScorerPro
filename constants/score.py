next_notes_char = " "
next_note_char = ","
note_duration_and_note_names_splitter_char = "-"
note_name_splitter_char = " "

note_name_to_staff_level = {"kick": 0, "floor_tom": 1, "snare": 2, "middle_tom": 2.5, "high_tom": 3}
staff_level_to_note_name = {value: key for key, value in note_name_to_staff_level.items()}
duration_to_text_duration = {1: "quarter", 2: "eighth", 4: "sixteenth"}
