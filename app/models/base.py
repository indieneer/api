import json
import datetime
from copy import deepcopy
from bson import ObjectId
from typing import Optional
from lib.db_utils import Serializable


class BaseDocument(Serializable):
    _id: ObjectId
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def __init__(
        self,
         **kwargs
        ) -> None:
        super().__init__()

        now = datetime.datetime.utcnow()

        self._id = kwargs.get("_id", ObjectId())
        self.created_at = kwargs.get("created_at", now)
        self.updated_at = kwargs.get("updated_at", now)

    def clone(self):
        copied = deepcopy(self)
        copied._id = ObjectId()
        return copied

    def __str__(self) -> str:
        return json.dumps(self.to_json())

    def __repr__(self) -> str:
        return self.__str__()
