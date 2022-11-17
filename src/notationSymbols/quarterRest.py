from kivy.cache import Cache

import notationSymbols
from notationSymbols import logger


class QuarterRest:
    @staticmethod
    def _get():
        quarterRestInfo = Cache.get("notationSymbols", "quarterRest", None)
        if quarterRestInfo is None:
            logger.log_dump(f"No symbol cached for \"quarterRest\", creating a new one...")

            quarterRestInfo = notationSymbols.build("quarterRest")
            Cache.append("notationSymbols", "quarterRest", quarterRestInfo)

        return quarterRestInfo

    @staticmethod
    def getInstructions():
        return QuarterRest._get()[0]

    @staticmethod
    def widthIfHeightIs(height):
        return QuarterRest._get()[1] * height
