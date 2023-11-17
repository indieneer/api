import json
from copy import deepcopy
from bson import ObjectId
from typing import Optional
from lib.db_utils import Serializable


class BaseDocument(Serializable):
    _id: ObjectId

    def __init__(self, _id: Optional[ObjectId] = None) -> None:
        super().__init__()

        self._id = _id if _id is not None else ObjectId()

    def clone(self):
        return deepcopy(self)

    def __str__(self) -> str:
        return json.dumps(self.as_json())

    def __repr__(self) -> str:
        return self.__str__()
