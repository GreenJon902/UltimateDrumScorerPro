import datetime

import app_info
from logger import colors

standard_tags = {"name": app_info.name, "author": app_info.author, "version": app_info.version,
                 "short_name": app_info.name_short}


# noinspection PyDefaultArgument
def standard_format(string: str, custom_tags: dict[str, any] = {}) -> str:
    datetime_time_now: datetime.datetime = datetime.datetime.now()
    time_now = {"year": datetime_time_now.year, "month": datetime_time_now.month, "day": datetime_time_now.day,
                "hour": datetime_time_now.hour, "minute": datetime_time_now.minute, "second": datetime_time_now.second,
                "microsecond": datetime_time_now.microsecond}
    tags = {}
    tags.update(standard_tags)
    tags.update(custom_tags)
    tags.update(time_now)
    return string.format(**tags)


# noinspection PyDefaultArgument
def colored_format(string: str, allow_color, custom_tags: dict[str, any] = {},
                   custom_colors: dict[str, str] = {}) -> str:
    string = standard_format(string, custom_tags=custom_tags)

    if allow_color:
        cols = {}
        cols.update(colors.str_to_code)
        cols.update(custom_colors)
        for color_name in cols:
            string = string.replace("%" + str(color_name), cols[color_name])

    else:
        cols = {}
        cols.update(colors.str_to_code)
        cols.update(custom_colors)
        for color_name in cols:
            string = string.replace("%" + str(color_name), "")

    return string


__all__ = ["standard_format", "colored_format"]
