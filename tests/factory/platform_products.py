from app.models import ModelsExtension
from app.models.platform_products import PlatformProduct, PlatformProductCreate, PlatformProductsModel
from app.services import Database
from bson import ObjectId
from typing import Union


class PlatformProductsFactory:
    db: Database
    model: PlatformProductsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, platform_product_id: ObjectId):
        self.db.connection[self.models.platform_products.collection].delete_one({
            "_id": platform_product_id})

    def create(self, input_data: Union[PlatformProduct, PlatformProductCreate]):
        if isinstance(input_data, PlatformProduct):
            platform_product = self.models.platform_products.put(input_data)
        else:
            platform_product = self.models.platform_products.create(input_data)

        return platform_product, lambda: self.cleanup(platform_product._id)
