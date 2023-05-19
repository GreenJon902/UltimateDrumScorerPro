import os

from kivy import Logger
from kivy.lang import Builder

kv_loaded = False
path = os.path.split(os.path.abspath(__file__))[0]

def check_kv():
    """
    Checks whether .kv files have been loaded, if not then they are loaded.
    """

    global kv_loaded

    if not kv_loaded:
        Logger.info("[UDSP] Loading .kv files...")
        for file in os.listdir(path):
            if "." in file and file.split(".")[1] == "kv":
                Logger.debug(f"[UDSP] Loading {file}")
                Builder.load_file(f"{path}/{file}")
        kv_loaded = True


__all__ = ["check_kv"]  # Can't have settings due to kv needing to be loaded first
