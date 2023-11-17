from __future__ import annotations
from typing import Dict, Any, cast

from bson import ObjectId


class Serializable(object):
    # serializes to dict preserving original types of values
    def to_json(self):
        return vars(self)

    # serializes to dict transforming values to JSON acceptable
    def as_json(self):
        return cast(Dict[str, Any], as_json(self.to_json()))

    def __eq__(self, other: Serializable) -> bool:
        return self.to_json() == other.to_json()


def as_json(thing: Any):
    if isinstance(thing, ObjectId):
        return str(thing)
    elif isinstance(thing, dict):
        for key, value in thing.items():
            thing[key] = as_json(value)

        return thing
    elif isinstance(thing, list):
        for idx, item in enumerate(thing):
            thing[idx] = as_json(item)

        return thing
    elif isinstance(thing, tuple):
        return as_json(list(thing))
    elif isinstance(thing, (int, float, bool, str)) or thing is None:
        return thing
    elif isinstance(thing, Serializable):
        return thing.as_json()
    else:
        return str(thing)
