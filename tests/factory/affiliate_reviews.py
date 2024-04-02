from app.models import ModelsExtension
from app.models.affiliate_reviews import AffiliateReview, AffiliateReviewCreate, AffiliateReviewsModel
from app.services import Database
from bson import ObjectId
from typing import Union

class AffiliateReviewsFactory:
    db: Database
    model: AffiliateReviewsModel

    def __init__(self, db: Database, models: ModelsExtension) -> None:
        self.db = db
        self.models = models

    def cleanup(self, affiliate_review_id: ObjectId):
        self.db.connection[self.models.affiliate_reviews.collection].delete_one({"_id": affiliate_review_id})

    def create(self, input_data: Union[AffiliateReview, AffiliateReviewCreate]):
        if isinstance(input_data, AffiliateReview):
            affiliate_review = self.models.affiliate_reviews.put(input_data)
        else:
            affiliate_review = self.models.affiliate_reviews.create(input_data)

        return affiliate_review, lambda: self.cleanup(affiliate_review._id)
