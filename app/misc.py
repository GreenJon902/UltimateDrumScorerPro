from kivy.app import App


def check_mode(mode: str):
    return App.get_running_app().check_mode(mode)
