from pymongo import ReturnDocument
from app.services import Database
from .exceptions import NotFoundException

from bson import ObjectId
from dataclasses import dataclass
from typing import Optional, List
from app.models.base import BaseDocument, Serializable


class AffiliateReview(BaseDocument):
    profile_id: ObjectId
    affiliate_id: ObjectId
    affiliate_platform_product_id: ObjectId
    text: Optional[str]
    rating: int

    def __init__(
        self,
        profile_id: ObjectId,
        affiliate_id: ObjectId,
        affiliate_platform_product_id: ObjectId,
        rating: int,
        text: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.profile_id = profile_id
        self.affiliate_id = affiliate_id
        self.affiliate_platform_product_id = affiliate_platform_product_id
        self.text = text
        self.rating = rating


@dataclass
class AffiliateReviewCreate(Serializable):
    profile_id: ObjectId
    affiliate_id: ObjectId
    affiliate_platform_product_id: ObjectId
    rating: int
    text: Optional[str] = None


@dataclass
class AffiliateReviewPatch(Serializable):
    profile_id: Optional[ObjectId] = None
    affiliate_id: Optional[ObjectId] = None
    affiliate_platform_product_id: Optional[ObjectId] = None
    text: Optional[str] = None
    rating: Optional[int] = None


class AffiliateReviewsModel:
    """
    Handles operations for the affiliate_reviews collection in the database.
    """

    db: Database
    collection: str = "affiliate_reviews"

    def __init__(self, db: Database) -> None:
        """
        Initializes the AffiliateReviewsModel with a database instance.

        :param Database db: The database instance used to interact with the affiliate_reviews collection.
        """
        self.db = db

    def get(self, review_id: str) -> Optional[AffiliateReview]:
        """
        Retrieve an affiliate review's details based on its ID.

        :param str review_id: The unique identifier of the affiliate review.
        :return: An instance of AffiliateReview initialized with the found review's details, or None if the review is not found.
        :rtype: Optional[AffiliateReview]
        """
        review_data = self.db.connection[self.collection].find_one({"_id": ObjectId(review_id)})
        if review_data:
            return AffiliateReview(**review_data)
        return None

    def get_all(self) -> List[AffiliateReview]:
        """
        Retrieve all affiliate reviews from the database.

        :return: A list of AffiliateReview objects representing all the reviews in the database.
        :rtype: List[AffiliateReview]
        """
        reviews = [AffiliateReview(**item) for item in self.db.connection[self.collection].find()]
        return reviews if reviews else []

    def create(self, input_data: AffiliateReviewCreate) -> AffiliateReview:
        """
        Create a new affiliate review in the database.

        :param AffiliateReviewCreate input_data: An object containing the data for the new affiliate review.
        :return: An instance of AffiliateReview initialized with the newly created review's details.
        :rtype: AffiliateReview
        """
        review_data = AffiliateReview(**input_data.to_json()).to_bson()
        self.db.connection[self.collection].insert_one(review_data)
        return AffiliateReview(**review_data)

    def put(self, affiliate_review: AffiliateReview) -> AffiliateReview:
        """
        Update an affiliate review in the database.

        :param affiliate_review: The affiliate review data to be updated.
        :type affiliate_review: AffiliateReview
        :return: The updated affiliate review data.
        :rtype: AffiliateReview
        """

        self.db.connection[self.collection].insert_one(affiliate_review.to_bson())
        return affiliate_review

    def patch(self, review_id: str, input_data: AffiliateReviewPatch) -> AffiliateReview:
        """
        Update an affiliate review in the database based on its ID.

        :param str review_id: The unique identifier of the affiliate review to be updated.
        :param AffiliateReviewPatch input_data: The data to update the review with.
        :return: The updated AffiliateReview object.
        :rtype: AffiliateReview
        :raises NotFoundException: If the review is not found.
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}
        updated_review = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(review_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        if updated_review:
            return AffiliateReview(**updated_review)
        else:
            raise NotFoundException("AffiliateReview")

    def delete(self, review_id: str) -> Optional[AffiliateReview]:
        """
        Delete an affiliate review from the database based on its ID.

        :param str review_id: The unique identifier of the affiliate review to be deleted.
        :return: An instance of AffiliateReview initialized with the deleted review's details, or None if no review is found.
        :rtype: Optional[AffiliateReview]
        :raises NotFoundException: If the review is not found.
        """
        review = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(review_id)}
        )
        if review:
            return AffiliateReview(**review)
        else:
            raise NotFoundException("AffiliateReview")

