from app.models import ModelsExtension
from app.models.comments import Comment, CommentCreate, CommentsModel
from app.services import Database
from bson import ObjectId
from typing import Union


class CommentsFactory:
    db: Database
    model: CommentsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, comment_id: ObjectId):
        self.db.connection[self.models.comments.collection].delete_one({
            "_id": comment_id})

    def create(self, input_data: Union[Comment, CommentCreate]):
        if isinstance(input_data, Comment):
            comment = self.models.comments.put(input_data)
        else:
            comment = self.models.comments.create(product_id=None, input_data=input_data)

        return comment, lambda: self.cleanup(comment._id)
