from app.models import ModelsExtension
from app.models.products import ProductCreate, ProductsModel
from app.services import Database
from bson import ObjectId


class ProductsFactory:
    db: Database
    model: ProductsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, product_id: ObjectId):
        self.db.connection[self.models.products.collection].delete_one({"_id": product_id})

    def create(self, input_data: ProductCreate):
        product = self.model.create(input_data)
        return product, lambda: self.cleanup(product._id)
