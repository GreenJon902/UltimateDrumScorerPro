def run():
    print("Starting...")
    import os

    os.environ["APPNAME"] = "UltimateDrumScorerPro"
    os.environ["APPAUTHOR"] = "GreenJon902"
    os.environ["APPVERSION"] = "v3.2"
    os.environ["SHORT_APPNAME"] = "UDSP"

    # ==================================================================================================================

    print("Setting up kivy...")
    os.environ["KCFG_INPUT_MOUSE"] = "mouse,multitouch_on_demand"
    # noinspection PyUnresolvedReferences
    import kivy
    kivy.require("2.1.0")

    import os, sys
    from kivy.resources import resource_add_path
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    from kivy.lang.builder import Builder
    Builder.load_file("misc.kv")

    # ==================================================================================================================


    print("Starting...")
    from ultimateDrumScorerProApp import UltimateDrumScorerProApp

    root = UltimateDrumScorerProApp()
    root.run()
    print("Finished!")


if __name__ == '__main__':
    run()
