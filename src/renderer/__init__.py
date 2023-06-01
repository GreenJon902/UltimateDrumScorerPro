from kivy.uix.relativelayout import RelativeLayout

from argumentTrigger import ArgumentTrigger
from scoreStorage import ScoreStorageItem


class Renderer(RelativeLayout):
    storage: ScoreStorageItem
    _storage: ScoreStorageItem = None  # Only used by getters and setter
    dispatch_instruction: callable = None

    def __init__(self, storage, **kwargs):
        self.dispatch_instruction = ArgumentTrigger(self.process_instructions, -1, give_combined=True)

        RelativeLayout.__init__(self, **kwargs)
        self.set_storage(storage)

    def process_instructions(self, instructions: list[tuple[tuple[any, ...], dict[str, any]]]):
        raise NotImplementedError()
    

    def get_storage(self):  # Use getters and setters so then subclasses can unbind from storage before it leaves.
        return self._storage
    def set_storage(self, storage):
        self._storage = storage
    storage = property(get_storage, set_storage)


__all__ = ["Renderer"]
