from kivy.clock import Clock


class ArgumentTrigger:  # Like a kivy clock trigger, but it takes arguments. Calls one time for each set of args
    callback: callable
    timeout: int
    give_combined: bool
    arg_list: list[tuple[tuple[any], dict[str, any]]]
    kivy_trigger = None

    def __init__(self, callback, timeout, give_combined=False):
        self.callback = callback
        self.timeout = timeout
        self.give_combined = give_combined

        self.arg_list = []
        self.kivy_trigger = Clock.create_trigger(self.dispatch, 0)

    def __call__(self, *args, **kwargs):  # We need to save the arguments, but we want them to be last in list
        arguments = args, kwargs
        if arguments in self.arg_list:
            self.arg_list.remove(arguments)  # Only ever one occurrence so only call once
        self.arg_list.append(arguments)
        self.kivy_trigger()

    def dispatch(self, _):
        if self.give_combined:
            self.callback(self.arg_list)
            self.arg_list.clear()
        else:
            for arguments in self.arg_list:
                self.callback(arguments)
            self.arg_list.clear()
