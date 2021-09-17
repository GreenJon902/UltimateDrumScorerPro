import logging
import os
# noinspection PyUnresolvedReferences
import sys
from copy import copy
from logging import Manager

import constants
from logger.classWithLogger import ClassWithLogger
from logger.consoleHandler import ConsoleHandler
from logger.fileHandler import FileHandler
# Setting up logger ----------------------------------------------------------------------------------------------------
from logger.format_funcs import standard_format
from logger.formatter import Formatter

logging.TRACE = 9
logging.DUMP = 10
logging.DEBUG = 11
# noinspection PyUnresolvedReferences
logging.addLevelName(logging.TRACE, "TRACE")
# noinspection PyUnresolvedReferences
logging.addLevelName(logging.DUMP, "DUMP")


logging.addLevelName(logging.DEBUG, "DEBUG")


root_logger = logging.getLogger("RootLogger")
# noinspection PyUnresolvedReferences
root_logger.setLevel(logging.TRACE)
# noinspection PyUnresolvedReferences,PyProtectedMember
root_logger.trace = lambda message, *args, **kws: \
    root_logger._log(logging.TRACE, message, args, **kws) if root_logger.isEnabledFor(logging.TRACE) else None
# noinspection PyUnresolvedReferences,PyProtectedMember
root_logger.dump = lambda message, *args, **kws: \
    root_logger._log(logging.DUMP, message, args, **kws) if root_logger.isEnabledFor(logging.DUMP) else None

console_handler = ConsoleHandler()
file_handler = FileHandler()
# noinspection PyUnresolvedReferences
console_handler.setLevel(logging.TRACE)
# noinspection PyUnresolvedReferences
file_handler.setLevel(logging.TRACE)


console_formatter = Formatter(use_color=True)
file_formatter = Formatter(use_color=False)
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)


root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# Set our logger to the default ----------------------------------------------------------------------------------------
# noinspection PyTypeChecker
logging.Logger.manager = Manager(root_logger)

# Testing --------------------------------------------------------------------------------------------------------------
root_logger.critical(standard_format("Welcome to {name}"))
root_logger.error(standard_format("Version {version}"))
root_logger.warning(standard_format("Made by {author}"))
root_logger.info(f"Logger setup and saving to {file_handler.path}")
# noinspection SpellCheckingInspection
root_logger.debug("Idk what to put here sooo...")
root_logger.trace(" 0 /    |  |  +---  |   |   +--+")
root_logger.dump("/|'     +--+  +--   |   |   |  |")
root_logger.trace("/ \\     |  |  +---  +-  +-  +--+")
root_logger.dump("")


if "LOG_LEVEL" in os.environ:
    root_logger.info(f"Setting log level to {os.environ.get('LOG_LEVEL')}")
    console_handler.setLevel(int(os.environ.get("LOG_LEVEL")))
else:
    root_logger.warning(f"No log level in environ, defaulting to {constants.logging.default_log_level}")
    console_handler.setLevel(constants.logging.default_log_level)

# ----------------------------------------------------------------------------------------------------------------------


def get_logger(name: str) -> ClassWithLogger:
    root_logger.dump(f"Creating logger with name \"{name}\"")
    return ClassWithLogger(name)


def push_name_to_logger_name_stack(function: callable):
    def wrapper(self, *args, **kwargs):
        self.push_logger_name(function.__name__)
        result = function(self, *args, **kwargs)
        self.pop_logger_name()

        return result
    return wrapper


def reset_logger_name_stack_for_function(function: callable):
    def wrapper(self, *args, **kwargs):
        name_before = copy(self._logger_name_stack)
        self._logger_name_stack.clear()
        result = function(self, *args, **kwargs)
        self._logger_name_stack = name_before

        return result
    return wrapper


def push_name_to_logger_name_stack_custom(name: str):
    def decorator(function: callable):
        def wrapper(self, *args, **kwargs):
            self.push_logger_name(name)
            result = function(self, *args, **kwargs)
            self.pop_logger_name()

            return result
        return wrapper
    return decorator



__all__ = ["get_logger", "ClassWithLogger", "push_name_to_logger_name_stack"]
