from typing import Dict, Any

from bson import ObjectId


class Serializable:
    def to_json(self):
        return vars(self)

    def as_json(self):
        return as_json(self.to_json())


def as_json(thing: Dict[str, Any]):
    for key, value in thing.items():
        if isinstance(value, ObjectId):
            thing[key] = str(value)
        elif isinstance(value, dict):
            as_json(value)
        elif isinstance(value, list):
            for item in value:
                as_json(item)
        elif isinstance(value, Serializable):
            thing[key] = value.as_json()
        else:
            continue

    return thing
