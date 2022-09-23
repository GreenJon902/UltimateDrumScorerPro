import logging
from logging import Logger


class ClassWithLogger:
    _created = False
    _logger: Logger = None
    _logger_base_name: str = "GreenJon902IsPog"

    _logger_name_stack: list[str]

    def _create_logger(self):
        self._logger = logging.getLogger(self._logger_base_name)
        self._created = True
        self.log_dump("Created self")

    def _check_logger(self):
        if not self._created:
            self._create_logger()

    def __init__(self, name=None):
        if self._logger_base_name == "GreenJon902IsPog":
            if name is None:
                self._logger_base_name = self.__class__.__name__
            else:
                self._logger_base_name = str(name)


        self._logger_name_stack = list()
        self._check_logger()

    def set_logger_name(self, name: str):
        self._logger_base_name = name
        self._do_logger_name()
        self.log_trace(f"Set base name for self to \"{name}\"")

    def push_logger_name(self, name: str):
        self._logger_name_stack.append(name)
        self._do_logger_name()
        self.log_trace(f"Pushed name \"{name}\" to name stack")

    def pop_logger_name(self) -> str:
        last_name = self._logger_name_stack.pop(-1)
        self._do_logger_name()
        self.log_trace(f"Popped name \"{last_name}\" from name stack")

        return last_name


    def _do_logger_name(self):
        name = self._logger_base_name

        if len(self._logger_name_stack) > 0:
            name += ("." + ".".join(self._logger_name_stack))

        self._logger.name = name

    def log_dump(self, *messages):
        self._check_logger()
        # noinspection PyUnresolvedReferences,PyProtectedMember
        self._logger.log(logging.DUMP, " ".join([str(message) for message in messages]))

    def log_trace(self, *messages):
        self._check_logger()
        # noinspection PyUnresolvedReferences,PyProtectedMember
        self._logger.log(logging.TRACE, " ".join([str(message) for message in messages]))

    def log_debug(self, *messages):
        self._check_logger()
        self._logger.debug(" ".join([str(message) for message in messages]))

    def log_info(self, *messages):
        self._check_logger()
        self._logger.info(" ".join([str(message) for message in messages]))

    def log_warning(self, *messages):
        self._check_logger()
        self._logger.warning(" ".join([str(message) for message in messages]))

    def log_error(self, *messages):
        self._check_logger()
        self._logger.error(" ".join([str(message) for message in messages]))

    def log_critical(self, *messages):
        self._check_logger()
        self._logger.critical(" ".join([str(message) for message in messages]))


__all__ = ["ClassWithLogger"]


if __name__ == '__main__':
    import os
    os.environ["LOG_LEVEL"] = "0"

    # noinspection PyUnresolvedReferences
    import logger

    # noinspection PyRedeclaration
    logger = ClassWithLogger("TestLogger")
    logger.log_info("I should be called Test")

    logger.set_logger_name("Test2")
    logger.log_info("I should be called Test2")

    logger.push_logger_name("Foo")
    logger.log_info("I should be called Test2.Foo")

    logger.push_logger_name("Bar")
    logger.log_info("I should be called Test2.Foo.Bar")

    n = logger.pop_logger_name()
    logger.log_info(f"I should be called Test2.Foo and also \"{n}\" should be \"Bar\"")
