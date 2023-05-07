from kivy.event import EventDispatcher


class ScoreStorageItemMetaclass(type):
    def __init__(cls, name, bases, attrs):
        super(ScoreStorageItemMetaclass, cls).__init__(name, bases, attrs)
        storage_item_types[cls.__name__] = cls


storage_item_types: dict[str, "ScoreStorageItem"] = {}
ScoreStorageItemBase = ScoreStorageItemMetaclass('ScoreStorageItemBase', (EventDispatcher, ), {})


class ScoreStorageItem(ScoreStorageItemBase):
    def __init__(self, **kwargs):
        ScoreStorageItemBase.__init__(self, **kwargs)

    def serialize(self) -> dict[str, any]:
        raise NotImplementedError()

    @staticmethod
    def deserialize(serialized: dict[str, any]) -> "ScoreStorageItem":
        raise NotImplementedError()


__all__ = ["ScoreStorageItem", "storage_item_types"]
