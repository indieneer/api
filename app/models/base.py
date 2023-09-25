from bson import ObjectId
from typing import Optional

from lib.db_utils import as_json


class Serializable():
    def to_json(self):
        return vars(self)

    def as_json(self):
        return as_json(self.to_json())


class BaseDocument(Serializable):
    _id: ObjectId

    def __init__(self, _id: Optional[ObjectId] = None) -> None:
        super().__init__()

        self._id = _id if _id is not None else ObjectId()
