import os
import sys

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].startswith("log_level="):
        os.environ["LOG_LEVEL"] = sys.argv[1].split("=")[1]

    # noinspection PyUnresolvedReferences
    import logger


    base_logger = logger.get_logger("BaseLogger")

    base_logger.log_info("Starting")
    base_logger.log_trace("Importing UI")
    import ui
    base_logger.log_debug("Imported UI successfully")
    base_logger.log_trace("Setting up")
    ui.setup()
    base_logger.log_debug("Setup successfully")
    base_logger.log_trace("Starting")
    ui.start()
    base_logger.log_info("Finished")

