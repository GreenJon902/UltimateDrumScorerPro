from logging import StreamHandler as _StreamHandler


class ConsoleHandler(_StreamHandler):
    pass


__all__ = ["ConsoleHandler"]
