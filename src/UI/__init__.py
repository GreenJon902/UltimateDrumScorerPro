from betterLogger import ClassWithLogger, push_name_to_logger_name_stack_custom

from UI.root import Root

logger = ClassWithLogger("UI")


def registerWidgets():
    logger.push_logger_name("registerWidgets")
    logger.log_debug("Registering widgets...")
    logger.log_info("Registered widgets!")
    logger.pop_logger_name()


def start():
    registerWidgets()

    root = Root()
    logger.log_dump("Root instance created, running...")
    root.run()


__all__ = ["start"]
