import copy
from logging import Formatter as _Formatter

from app_info.logging_info import log_format
from logger import colors
from logger.format_funcs import colored_format


class Formatter(_Formatter):
    def __init__(self, use_color=False):
        _Formatter.__init__(self)
        self.use_color = use_color

    def format(self, record):
        record = copy.deepcopy(record)
        record.msg = colored_format(log_format, self.use_color,
                                    custom_tags={"message": record.msg, "logger": self, "level": record.levelname,
                                                 "class_name": record.name},
                                    custom_colors={"LEVEL_COLOR": colors.level_to_code[record.levelname]})
        return _Formatter.format(self, record)


__all__ = ["Formatter"]
