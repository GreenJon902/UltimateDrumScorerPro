import os.path
from logging import FileHandler as _FileHandler

from app_info import logging_info
from logger.format_funcs import standard_format


class FileHandler(_FileHandler):
    def __init__(self, encoding=None, delay=False):
        if not os.path.exists(logging_info.save_dir):
            os.makedirs(logging_info.save_dir)

        file_name = standard_format(logging_info.save_name, custom_tags={"number": "{number}"})  # A rather hacky fix
        path = os.path.join(logging_info.save_dir, file_name)

        if "{number}" in file_name:
            n = 0
            while True:
                filename = path.replace("{number}", str(n))
                if not os.path.exists(filename):
                    break
                n += 1
                if n > 1000:  # prevent maybe flooding ?
                    raise Exception("Too many logs, remove them")

            file_name = standard_format(logging_info.save_name, custom_tags={"number": n})
            path = os.path.join(logging_info.save_dir, file_name)

        _FileHandler.__init__(self, path, mode="w", encoding=encoding, delay=delay)
        self.path = path


__all__ = ["FileHandler"]
