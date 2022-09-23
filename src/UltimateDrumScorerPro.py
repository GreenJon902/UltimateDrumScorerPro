def startup():
    print("Starting...")
    import os
    import sys
    stderr = sys.stderr

    if len(sys.argv) >= 2 and sys.argv[1].startswith("log_level="):
        os.environ["LOG_LEVEL"] = sys.argv[1].split("=")[1]

    os.environ["APPNAME"] = "UltimateDrumScorerPro"
    os.environ["APPAUTHOR"] = "GreenJon902"
    os.environ["APPVERSION"] = "v2.0"
    os.environ["SHORT_APPNAME"] = "UDSP"

    import betterLogger
    base_logger = betterLogger.get_logger("BaseLogger")

    # ==================================================================================================================

    base_logger.log_info("Setting up kivy")
    os.environ["KIVY_NO_FILELOG"] = "True"
    os.environ["KIVY_NO_CONSOLELOG"] = "True"
    os.environ["KCFG_INPUT_MOUSE"] = "mouse,multitouch_on_demand"
    base_logger.log_dump("Set ENV variables \"KIVY_NO_FILELOG\" and \"KIVY_NO_CONSOLELOG\" too True | "
                         "\"KCFG_INPUT_MOUSE\" set too \"mouse,multitouch_on_demand\"")
    # noinspection PyUnresolvedReferences
    import kivy
    from kivy.logger import Logger
    sys.stderr = stderr  # revert back # TODO: Fix this
    Logger.setLevel(betterLogger.config.log_level)
    base_logger.log_info("Set up kivy")

    # ==================================================================================================================

    base_logger.log_info("Starting...")
    import UI
    UI.start()
    base_logger.log_info("Finished!")


if __name__ == "__main__":
    startup()
