from betterLogger import ClassWithLogger

from UI.root import Root

logger = ClassWithLogger("UI")
root: Root


def registerWidgets():
    logger.push_logger_name("registerWidgets")
    logger.log_debug("Registering widgets...")
    logger.log_info("Registered widgets!")
    logger.pop_logger_name()


def prepare():
    global root

    registerWidgets()

    root = Root()
    logger.log_dump("Root instance created")


def start():
    root.run()


__all__ = ["start"]
