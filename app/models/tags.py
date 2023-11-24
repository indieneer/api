from typing import Optional
from bson import ObjectId
from dataclasses import dataclass

from pymongo import ReturnDocument

from app.services import Database
from . import BaseDocument, Serializable


class Tag(BaseDocument):
    name: str

    def __init__(
        self,
        name: str,
        _id: Optional[ObjectId] = None,
        **kwargs
    ) -> None:
        super().__init__(_id)

        self.name = name


@dataclass
class TagCreate(Serializable):
    name: str


@dataclass
class TagPatch(Serializable):
    name: Optional[str] = None


class TagsModel:
    db: Database
    collection: str = "tags"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, tag_id: str):
        tag = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(tag_id)}
        )

        if tag is not None:
            return Tag(**tag)

    def get_all(self):
        tags = [Tag(**item) for item in self.db.connection[self.collection].find()]
        if tags is not None:
            return tags

    def create(self, input_data: TagCreate):
        tag = Tag(**input_data.to_json()).to_json()
        self.db.connection[self.collection].insert_one(tag)

        return Tag(**tag)

    def patch(self, tag_id: str, input_data: TagPatch):
        return Tag(**self.db.connection[self.collection].find_one_and_update({"_id": ObjectId(tag_id)}, {"$set": input_data.to_json()}, return_document=ReturnDocument.AFTER))

    def delete(self, tag_id: str):
        tag = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(tag_id)}
        )

        if tag is not None:
            return Tag(**tag)
