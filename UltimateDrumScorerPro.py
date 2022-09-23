import os
import sys

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].startswith("log_level="):
        os.environ["LOG_LEVEL"] = sys.argv[1].split("=")[1]

    # noinspection PyUnresolvedReferences
    import logger
    base_logger = logger.get_logger("BaseLogger")


    base_logger.log_info("Setting up PIL")

    # noinspection PyUnresolvedReferences
    import PIL
    from PIL.Image import init as PilInit
    PilInit()

    base_logger.log_info("Set up PIL")


    base_logger.log_info("Setting up kivy")
    os.environ["KIVY_NO_FILELOG"] = "True"
    os.environ["KIVY_NO_CONSOLELOG"] = "True"
    os.environ["KCFG_INPUT_MOUSE"] = "mouse,multitouch_on_demand"
    base_logger.log_dump("Set ENV variables \"KIVY_NO_FILELOG\" and \"KIVY_NO_CONSOLELOG\" too True | "
                         "\"KCFG_INPUT_MOUSE\" set too \"mouse,multitouch_on_demand\"")
    # noinspection PyUnresolvedReferences
    import kivy
    from kivy.logger import Logger

    try:
        Logger.setLevel(int(os.environ["LOG_LEVEL"]))
    except KeyError:
        import constants
        Logger.setLevel(constants.logging.default_log_level)

    base_logger.log_info("Set up kivy")


    base_logger.log_info("Starting")
    import app
    app.start()
    base_logger.log_info("Finished")
