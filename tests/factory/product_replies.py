from app.models import ModelsExtension
from app.models.product_replies import ProductReply, ProductReplyCreate, ProductRepliesModel
from app.services import Database
from bson import ObjectId
from typing import Union


class ProductRepliesFactory:
    db: Database
    model: ProductRepliesModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, product_reply_id: ObjectId):
        self.db.connection[self.models.product_replies.collection].delete_one({
            "_id": product_reply_id})

    def create(self, input_data: Union[ProductReply, ProductReplyCreate]):
        if isinstance(input_data, ProductReply):
            product_reply = self.models.product_replies.put(input_data)
        else:
            product_reply = self.models.product_replies.create(input_data=input_data)

        return product_reply, lambda: self.cleanup(product_reply._id)

