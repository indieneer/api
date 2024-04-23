from app.models import ModelsExtension
from app.models.affiliate_platform_products import AffiliatePlatformProduct, AffiliatePlatformProductCreate, AffiliatePlatformProductsModel
from app.services import Database
from bson import ObjectId
from typing import Union


class AffiliatePlatformProductsFactory:
    db: Database
    model: AffiliatePlatformProductsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, affiliate_platform_product_id: ObjectId):
        self.db.connection[self.models.affiliate_platform_products.collection].delete_one({
            "_id": affiliate_platform_product_id})

    def create(self, input_data: Union[AffiliatePlatformProduct, AffiliatePlatformProductCreate]):
        if isinstance(input_data, AffiliatePlatformProduct):
            affiliate_platform_product = self.models.affiliate_platform_products.put(input_data)
        else:
            affiliate_platform_product = self.models.affiliate_platform_products.create(input_data)

        return affiliate_platform_product, lambda: self.cleanup(affiliate_platform_product._id)

