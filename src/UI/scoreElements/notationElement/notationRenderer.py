from __future__ import annotations
import typing

import betterLogger
from kivy.cache import Cache
from kivy.graphics import Rectangle, Color
from kivy.graphics.instructions import Canvas, InstructionGroup
from kivy.core.text import Label as CoreLabel
from kivy.graphics.texture import Texture

if typing.TYPE_CHECKING:
    from notationTree import Bar
    from config.notationConfig import NotationRendererConfig

logger = betterLogger.get_logger("notationRenderer.official")


def renderLine(notes: list[Bar], config: NotationRendererConfig) -> Canvas:
    canvas = Canvas()

    measureLength = None
    subdivisionQuantifier = None
    for barNumber, bar in enumerate(notes):
        logger.push_logger_name(str(barNumber))
        logger.log_debug(f"Rendering bar {barNumber}/{len(notes)}...")

        if (config.timeSignatureConfig.alwaysDrawTimeSignature or
                (measureLength != bar.measureLength and subdivisionQuantifier != bar.subdivisionQuantifier and
                 config.timeSignatureConfig.drawTimeSignatureOnChange)):
            measureLength = bar.measureLength
            subdivisionQuantifier = bar.subdivisionQuantifier

            instructions, width = getTimeSignature(measureLength, subdivisionQuantifier, config)
            canvas.add(Color(rgba=config.timeSignatureConfig.color))
            canvas.add(instructions)
            logger.log_debug(f"Added new time signature of {measureLength}/{subdivisionQuantifier}")

        logger.log_trace(f"Rendered bar")
        logger.pop_logger_name()

    return canvas


def getTimeSignature(measureLength, subdivisionQuantifier, config):
    measureLengthTexture: Texture = Cache.get("UI.score.notation.timeSignature", str(measureLength), None)
    if measureLengthTexture is None:
        logger.log_dump(f"No texture cached for {measureLength}, creating a new one...")

        coreLabel = CoreLabel(str(measureLength), font_size=config.timeSignatureConfig.fontSize)
        coreLabel.refresh()
        measureLengthTexture = coreLabel.texture
        Cache.append("UI.score.notation.timeSignature", str(measureLength), measureLengthTexture)

    subdivisionQuantifierTexture: Texture = Cache.get("UI.score.notation.timeSignature", str(subdivisionQuantifier),
                                                      None)
    if subdivisionQuantifierTexture is None:
        logger.log_dump(f"No texture cached for {subdivisionQuantifier}, creating a new one...")

        coreLabel = CoreLabel(str(subdivisionQuantifier), font_size=config.timeSignatureConfig.fontSize)
        coreLabel.refresh()
        subdivisionQuantifierTexture = coreLabel.texture
        Cache.append("UI.score.notation.timeSignature", str(subdivisionQuantifier), subdivisionQuantifierTexture)

    width = max(measureLengthTexture.width, subdivisionQuantifierTexture.width)
    instructionGroup = InstructionGroup()
    instructionGroup.add(Rectangle(pos=((width-measureLengthTexture.width)/2, 0),
                                   size=measureLengthTexture.size,
                                   texture=measureLengthTexture))
    instructionGroup.add(Rectangle(pos=((width-subdivisionQuantifierTexture.width)/2,
                                        -subdivisionQuantifierTexture.height),
                                   size=subdivisionQuantifierTexture.size,
                                   texture=subdivisionQuantifierTexture))

    return instructionGroup, width
