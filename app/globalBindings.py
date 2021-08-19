# Basics from https://github.com/GreenJon902/SpaceBuilderMergeGame/blob/master/lib/globalEvents.py
from logger import ClassWithLogger

logger = ClassWithLogger(name="GlobalEvents")


class GlobalBindings:
    bindings: dict[str, list] = {}

    @classmethod
    def bind(cls, **kwargs):
        for event_name, function in kwargs.items():
            cls.check_binding(event_name)

            cls.bindings[event_name].append(function)
            logger.log_dump(function, "was bound to event '", event_name, "'")

    @classmethod
    def register(cls, event_name: str):
        cls.bindings[event_name] = list()
        logger.log_debug("Event '", event_name, "' has been created")

    @classmethod
    def dispatch(cls, event_name: str, *args, **kwargs):
        cls.check_binding(event_name)
        if len(cls.bindings[event_name]) != 0:
            for function in cls.bindings[event_name]:
                function(*args, **kwargs)

        else:
            logger.log_warning(f"No functions bound to event {event_name}")

    @classmethod
    def check_binding(cls, event_name: str):
        if event_name not in cls.bindings:
            cls.register(event_name)


__all__ = ["GlobalBindings"]
