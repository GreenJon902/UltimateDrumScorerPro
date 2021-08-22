reset = "\033[0m"
bold = "\033[1m"

color_changer_thing = "\033[1;%dm"
black, red, green, yellow, blue, magenta, cyan, white = [color_changer_thing % (30 + i) for i in range(8)]

str_to_code = {
    "RESET": reset,
    "BOLD": bold,
    "BLACK": black,
    "RED": red,
    "GREEN": green,
    "YELLOW": yellow,
    "BLUE": blue,
    "MAGENTA": magenta,
    "CYAN": cyan,
    "WHITE": white
}

level_to_code = {
    "CRITICAL": red + bold,
    "ERROR": red,
    "WARNING": yellow,
    "INFO": green,
    "DEBUG": cyan,
    "DUMP": blue,
    "TRACE": black
}


__all__ = ["reset", "bold", "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "str_to_code",
           "level_to_code"]
