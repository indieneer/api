from app.models import ModelsExtension
from app.models.operating_systems import OperatingSystem, OperatingSystemCreate, OperatingSystemsModel
from app.services import Database
from bson import ObjectId
from typing import Union


class OperatingSystemsFactory:
    db: Database
    model: OperatingSystemsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, operating_system_id: ObjectId):
        self.db.connection[self.models.operating_systems.collection].delete_one({
                                                                                  "_id": operating_system_id})

    def create(self, input_data: Union[OperatingSystem, OperatingSystemCreate]):
        if isinstance(input_data, OperatingSystem):
            operating_system = self.models.operating_systems.put(input_data)
        else:
            operating_system = self.models.operating_systems.create(input_data)

        return operating_system, lambda: self.cleanup(operating_system._id)
