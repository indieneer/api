from __future__ import annotations
from typing import Dict, Any, cast

from bson import ObjectId


class Serializable(object):
    def to_json(self):
        """Recursively converts types into JSON compatible

        Returns:
            Dict[str, Any]: A dict containing all of the fields from the original class
        """
        return cast(Dict[str, Any], to_json(self))

    def to_dict(self):
        """Recursively unpacks serializable fields into a dict. Preserves the original type of each field.

        Returns:
            Dict[str, Any]:  A dict containing all of the fields from the original class
        """
        return cast(Dict[str, Any], to_dict(self))

    def to_bson(self):
        """Recursively converts types into BSON compatible

        Returns:
            Dict[str, Any]:  A dict containing all of the fields from the original class
        """
        return cast(Dict[str, Any], to_bson(self))

    def __eq__(self, other: Serializable) -> bool:
        return self.to_json() == other.to_json()


def to_json(thing: Any):
    if isinstance(thing, ObjectId):
        return str(thing)
    elif isinstance(thing, dict):
        for key, value in thing.items():
            thing[key] = to_json(value)

        return thing
    elif isinstance(thing, list):
        for idx, item in enumerate(thing):
            thing[idx] = to_json(item)

        return thing
    elif isinstance(thing, tuple):
        return to_json(list(thing))
    elif isinstance(thing, (int, float, bool, str)) or thing is None:
        return thing
    elif isinstance(thing, Serializable):
        return to_json(vars(thing))
    else:
        return str(thing)

def to_dict(thing: Any):
    if isinstance(thing, Serializable):
        return to_dict(vars(thing))
    elif isinstance(thing, dict):
        for key, value in thing.items():
            thing[key] = to_dict(value)

        return thing
    elif isinstance(thing, list):
        for idx, item in enumerate(thing):
            thing[idx] = to_dict(item)

        return thing
    elif isinstance(thing, tuple):
        return to_dict(list(thing))
    else:
        return thing

def to_bson(thing: Any):
    if isinstance(thing, ObjectId):
        return thing
    elif isinstance(thing, dict):
        for key, value in thing.items():
            thing[key] = to_bson(value)

        return thing
    elif isinstance(thing, list):
        for idx, item in enumerate(thing):
            thing[idx] = to_bson(item)

        return thing
    elif isinstance(thing, tuple):
        return to_bson(list(thing))
    elif isinstance(thing, (int, float, bool, str)) or thing is None:
        return thing
    elif isinstance(thing, Serializable):
        return to_bson(vars(thing))
    else:
        return str(thing)