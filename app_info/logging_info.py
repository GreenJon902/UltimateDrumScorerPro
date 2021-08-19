import app_info

save_dir = app_info.dirs.user_log_dir
save_name = "{name}_{year}-{day}-{hour}-{minute}_{number}.log"

log_format = \
    "%LEVEL_COLOR[%BOLD{level: <10}]%RESET %LEVEL_COLOR[%BOLD{class_name: <32}]%RESET %LEVEL_COLOR {message}%RESET"

default_log_level = 10

custom_name_per_log_array = {"kivy": "Kivy.%s"}

__all__ = ["save_dir", "save_name", "log_format", "default_log_level", "custom_name_per_log_array"]
