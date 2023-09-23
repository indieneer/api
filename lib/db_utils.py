from typing import Dict, Any

from bson import ObjectId


def as_json(thing: Dict[str, Any]):
    for key, value in thing.items():
        if isinstance(value, ObjectId):
            thing[key] = str(value)
        elif isinstance(value, dict):
            as_json(value)
        elif isinstance(value, list):
            for item in value:
                as_json(item)
        else:
            continue

    return thing
