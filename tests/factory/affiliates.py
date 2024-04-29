from app.models import ModelsExtension
from app.models.affiliates import Affiliate, AffiliateCreate, AffiliatesModel
from app.services import Database
from bson import ObjectId
from typing import Union

class AffiliatesFactory:
    db: Database
    model: AffiliatesModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, affiliate_id: ObjectId):
        self.db.connection[self.models.affiliates.collection].delete_one({"_id": affiliate_id})

    def create(self, input_data: Union[Affiliate, AffiliateCreate]):
        if isinstance(input_data, Affiliate):
            affiliate = self.models.affiliates.put(input_data)
        else:
            affiliate = self.models.affiliates.create(input_data)

        return affiliate, lambda: self.cleanup(affiliate._id)
