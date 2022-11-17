import betterLogger
import os

from kivy.cache import Cache

from notationSymbols.instructionMakers import *

logger = betterLogger.get_logger("notationSymbols.builder")


def build(name):
    logger.push_logger_name(f"build")
    logger.log_debug(f"Loading \"{name}.ns\"")

    lines = open(os.path.join("resources/notationSymbols", name + ".ns"), "r").read().split(os.linesep)
    fileType = lines.pop(0)

    if fileType == "!STATIC":
        ret = buildStatic(lines)
    else:
        raise Exception(f"File \"{name}\" has unknown type")

    logger.pop_logger_name()
    return ret





def buildStatic(lines):
    logger.push_logger_name("static")

    instructions = []
    height_to_width_ratio: float

    for n, line in enumerate(lines):
        if line.startswith(";") or line == "" or line.isspace():
            logger.log_trace(f"Line {n} is empty")
            continue
        splitLine = line.split(" ")
        command = splitLine.pop(0)
        args = splitLine

        for i, arg in enumerate(args):
            args[i] = eval(arg)

        logger.log_dump(f"Line {n} is \"{command}\" and has args {args}")

        if command == "PushMatrix":
            instructions.append(makePushMatrixInstruction(*args))
        elif command == "Scale":
            instructions.append(makeScaleInstruction(*args))
        elif command == "Translate":
            instructions.append(makeTranslateInstruction(*args))
        elif command == "PopMatrix":
            instructions.append(makePopMatrixInstruction(*args))
        elif command == "Image":
            instructions.append(makeImageInstruction(*args))
        elif command == "HEIGHT_TO_WIDTH_RATIO":
            height_to_width_ratio = float(args[0])
        else:
            raise NotImplemented(command)

    logger.log_dump(f"Built Instructions: {instructions}")
    logger.log_dump(f"Height to width ratio: {height_to_width_ratio}")
    logger.pop_logger_name()

    return instructions, height_to_width_ratio



def prepare():
    Cache.register("notationSymbols")



if __name__ == "__main__":
    prepare()
    build("quarterRest")
