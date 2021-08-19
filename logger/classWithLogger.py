import logging
from logging import Logger


class ClassWithLogger:
    _created = False
    _logger: Logger = None
    _logger_name: str = "GreenJon902IsPog"

    def _create_logger(self):
        self._logger = logging.getLogger(self._logger_name)
        self._created = True
        self.log_dump("Created self")

    def _check_logger(self):
        if not self._created:
            self._create_logger()

    def __init__(self, name=None):
        if self._logger_name == "GreenJon902IsPog":
            if name is None:
                self._logger_name = self.__class__.__name__
            else:
                self._logger_name = str(name)

        self._check_logger()

    def set_logger_name(self, name: str):
        self._logger.name = name
        self.log_dump(f"Set name for self to \"{name}\"")

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
