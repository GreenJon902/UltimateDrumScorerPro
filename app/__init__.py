import logger
from app.ultimateDrumScorerProApp import UltimateDrumScorerProApp


app_logger = logger.get_logger("App")


def start():
    app = UltimateDrumScorerProApp()
    app_logger.log_dump("Instance created, running...")
    app.run()
