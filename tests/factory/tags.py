from app.models import ModelsExtension
from app.models.tags import Tag, TagCreate, TagsModel
from app.services import Database
from bson import ObjectId
from typing import Union


class TagsFactory:
    db: Database
    model: TagsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, tag_id: ObjectId):
        self.db.connection[self.models.tags.collection].delete_one({
                                                                       "_id": tag_id})

    def create(self, input_data: Union[Tag, TagCreate]):
        if isinstance(input_data, Tag):
            tag = self.models.tags.put(input_data)
        else:
            tag = self.models.tags.create(input_data)

        return tag, lambda: self.cleanup(tag._id)
