from app.models import ModelsExtension
from app.models.product_comments import ProductComment, ProductCommentCreate, ProductCommentsModel
from app.services import Database
from bson import ObjectId
from typing import Union


class ProductCommentsFactory:
    db: Database
    model: ProductCommentsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, product_comment_id: ObjectId):
        self.db.connection[self.models.product_comments.collection].delete_one({
            "_id": product_comment_id})

    def create(self, input_data: Union[ProductComment, ProductCommentCreate]):
        if isinstance(input_data, ProductComment):
            product_comment = self.models.product_comments.put(input_data)
        else:
            product_comment = self.models.product_comments.create(input_data=input_data)

        return product_comment, lambda: self.cleanup(product_comment._id)
