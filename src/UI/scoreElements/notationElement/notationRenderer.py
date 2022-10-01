from __future__ import annotations
import typing

import betterLogger
from kivy.cache import Cache
from kivy.graphics import *
from kivy.core.text import Label as CoreLabel
from kivy.graphics.texture import Texture


if typing.TYPE_CHECKING:
    from notationTree import Bar
    from config.notationConfig import NotationRendererConfig

logger = betterLogger.get_logger("notationRenderer.official")


def renderLine(notes: list[Bar], config: NotationRendererConfig) -> Canvas:
    canvas = Canvas()

    with canvas:
        x_offset = 0



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

                logger.log_debug(f"Time signature changed to {measureLength}/{subdivisionQuantifier}")

                x_offset += config.timeSignatureConfig.bufferSpace.before

                PushMatrix()
                Translate(x_offset, 0)
                x_offset += drawTimeSignature(measureLength, subdivisionQuantifier, config)
                PopMatrix()

                x_offset += config.timeSignatureConfig.bufferSpace.after





            beatNumber = 0
            while beatNumber < bar.measureLength:
                beat = bar.getContent()[beatNumber]

                logger.push_logger_name(str(beatNumber))
                logger.log_dump(f"Rendering beat {beatNumber}")

                if beat is None:
                    logger.log_debug("Beat has no contents, rendering quarter rest")
                    x_offset += config.restConfig.bufferSpace.before

                    PushMatrix()
                    Translate(x_offset, 0)
                    x_offset += drawQuarterRest(config)
                    PopMatrix()

                    x_offset += config.restConfig.bufferSpace.after


                else:
                    beat_contents = beat.flatten()

                    x_offset += config.beatConfig.bufferSpace.before
                    PushMatrix()
                    Translate(x_offset, 0)
                    x_offset += drawBeatContents(beat_contents, config)
                    PopMatrix()
                    x_offset += config.beatConfig.bufferSpace.after


                beatNumber += 1
                logger.log_dump(f"Rendered beat!")
                logger.pop_logger_name()

            logger.log_dump(f"Rendered bar")
            logger.pop_logger_name()

        for i in range(5):
            y = i * config.barConfig.staffSpacing - config.barConfig.staffSpacing * 2
            Line(points=(0, y, x_offset, y))

    return canvas



def drawBeatContents(beat_contents, config):
    x_offset = 0

    for notes_index, (notes_depth, note_names) in enumerate(beat_contents):
        logger.log_dump(f"Rendering sub-beat {notes_index} - notes_depth={notes_depth}, "
                        f"notes={note_names}")
        for note_name in note_names:
            x_offset += drawNoteHead(note_name, config)

    return x_offset



def drawNoteHead(note_name, config):
    if note_name in config.noteHeadConfig.round_heads:
        Ellipse(pos=(0, config.barConfig.staffSpacing * (config.noteHeadConfig.noteHeadLevel[note_name] - 1) -
                     config.barConfig.staffSpacing * 2),
                size=(config.noteHeadConfig.roundNoteHead.width, config.noteHeadConfig.roundNoteHead.height))
        return config.noteHeadConfig.roundNoteHead.width


def drawQuarterRest(config):
    Rectangle(pos=(0, -config.restConfig.quarterRestHeight/2),
              size=(204/584 * config.restConfig.quarterRestHeight, config.restConfig.quarterRestHeight),
              source="resources/quarterRest.png")
    return 204/584 * config.restConfig.quarterRestHeight


def drawTimeSignature(measureLength, subdivisionQuantifier, config):
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


    Color(rgba=config.timeSignatureConfig.color)

    width = max(measureLengthTexture.width, subdivisionQuantifierTexture.width)
    Rectangle(pos=((width - measureLengthTexture.width) / 2, 0),
              size=measureLengthTexture.size,
              texture=measureLengthTexture)
    Rectangle(pos=((width - subdivisionQuantifierTexture.width) / 2,
                   -subdivisionQuantifierTexture.height),
              size=subdivisionQuantifierTexture.size,
              texture=subdivisionQuantifierTexture)

    return width
