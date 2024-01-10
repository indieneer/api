from app.models import ModelsExtension
from app.models.products import Product, ProductCreate, ProductsModel
from app.services import Database
from bson import ObjectId
from typing import Union

class ProductsFactory:
    db: Database
    model: ProductsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, product_id: ObjectId):
        self.db.connection[self.models.products.collection].delete_one({
                                                                       "_id": product_id})

    def create(self, input_data: Union[Product, ProductCreate]):
        if isinstance(input_data, Product):
            product = self.models.products.put(input_data)
        else:
            product = self.models.products.create(input_data)

        return product, lambda: self.cleanup(product._id)
