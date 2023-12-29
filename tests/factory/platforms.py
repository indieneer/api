from app.models import ModelsExtension
from app.models.platforms import Platform, PlatformCreate, PlatformsModel
from app.services import Database
from bson import ObjectId
from typing import Union


class PlatformsFactory:
    db: Database
    model: PlatformsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, platform_id: ObjectId):
        self.db.connection[self.models.platforms.collection].delete_one({
                                                                          "_id": platform_id})

    def create(self, input_data: Union[Platform, PlatformCreate]):
        if isinstance(input_data, Platform):
            platform = self.models.platforms.put(input_data)
        else:
            platform = self.models.platforms.create(input_data)

        return platform, lambda: self.cleanup(platform._id)
