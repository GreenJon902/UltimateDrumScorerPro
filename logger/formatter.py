import copy
from logging import Formatter as _Formatter

import constants
from logger import colors
from logger.format_funcs import colored_format


class Formatter(_Formatter):
    def __init__(self, use_color=False):
        _Formatter.__init__(self)
        self.use_color = use_color

    def format(self, record):
        record = copy.deepcopy(record)

        if record.name in constants.logging.custom_name_per_log_array.keys():
            new_name, new_msg = record.msg.split(": ", maxsplit=1)

            record.name = str(constants.logging.custom_name_per_log_array[record.name]) % new_name
            record.msg = new_msg

        record.msg = colored_format(constants.logging.log_format, self.use_color,
                                    custom_tags={"message": record.msg, "logger": self, "level": record.levelname,
                                                 "class_name": record.name},
                                    custom_colors={"LEVEL_COLOR": colors.level_to_code[record.levelname]})
        return _Formatter.format(self, record)


__all__ = ["Formatter"]
