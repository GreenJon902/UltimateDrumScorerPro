from typing import Union

from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, DictProperty


class MultiDimDict(EventDispatcher):
    """A class like kivy's DictProperty but with multidimensional support"""


class Item(EventDispatcher):
    parent: "Item" = ObjectProperty()
    children: Union["Item", any] = DictProperty()


class RootItem(Item):
    pass
