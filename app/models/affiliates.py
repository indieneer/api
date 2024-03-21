from pymongo import ReturnDocument
from app.services import Database
from .exceptions import NotFoundException


from dataclasses import dataclass, field
from typing import Optional, List
from bson import ObjectId
from app.models.base import BaseDocument, Serializable


class Affiliate(BaseDocument):
    name: str
    sales: int
    bio: str
    enabled: bool
    logo_url: str
    reviews: List[ObjectId]

    def __init__(
        self,
        name: str,
        sales: int,
        bio: str,
        enabled: bool,
        logo_url: str,
        reviews: Optional[List[ObjectId]] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.sales = sales
        self.bio = bio
        self.enabled = enabled
        self.logo_url = logo_url
        self.reviews = reviews if reviews is not None else []


@dataclass
class AffiliateCreate(Serializable):
    name: str
    sales: int
    bio: str
    enabled: bool
    logo_url: str
    reviews: List[ObjectId] = field(default_factory=list)


@dataclass
class AffiliatePatch(Serializable):
    name: Optional[str] = None
    sales: Optional[int] = None
    bio: Optional[str] = None
    enabled: Optional[bool] = None
    logo_url: Optional[str] = None
    reviews: Optional[List[ObjectId]] = field(default_factory=list)


class AffiliatesModel:
    db: Database
    collection: str = "affiliates"

    def __init__(self, db: Database) -> None:
        """
        Initializes the AffiliatesModel with a database instance.

        :param Database db: The database instance used to interact with the affiliates collection.
        """
        self.db = db

    def get(self, affiliate_id: str) -> Optional[Affiliate]:
        """
        Retrieve an affiliate's details based on its ID.

        This method searches for an affiliate in the database using the provided affiliate_id.
        If found, it returns an Affiliate object initialized with the affiliate's details.

        :param str affiliate_id: The unique identifier of the affiliate.
        :return: An instance of Affiliate initialized with the found affiliate's details, or None if the affiliate is not found.
        :rtype: Affiliate | None
        """
        affiliate = self.db.connection[self.collection].find_one({"_id": ObjectId(affiliate_id)})

        if affiliate:
            return Affiliate(**affiliate)
        else:
            return None

    def get_all(self) -> List[Affiliate]:
        """
        Retrieve all affiliates from the database.

        This method fetches all affiliates from the database and returns them as a list of Affiliate objects.
        If there are no affiliates found, it returns an empty list.

        :return: A list of Affiliate objects representing all the affiliates in the database.
        :rtype: list[Affiliate]
        """
        affiliates = [Affiliate(**item) for item in self.db.connection[self.collection].find()]
        return affiliates if affiliates else []

    def create(self, input_data: AffiliateCreate) -> Affiliate:
        """
        Create a new affiliate in the database.

        This method takes the input data for a new affiliate and inserts the new affiliate into the database.
        It then returns an Affiliate object initialized with the newly created affiliate's details.

        :param AffiliateCreate input_data: An object containing the data for the new affiliate.
        :return: An instance of Affiliate initialized with the newly created affiliate's details.
        :rtype: Affiliate
        """
        affiliate_data = Affiliate(**input_data.to_json()).to_bson()
        self.db.connection[self.collection].insert_one(affiliate_data)
        return Affiliate(**affiliate_data)

    def patch(self, affiliate_id: str, input_data: AffiliatePatch) -> Affiliate:
        """
        Update an affiliate in the database based on its ID.

        This method updates the affiliate specified by the affiliate ID using the provided input data.
        Only the fields provided in the input_data are updated; others are left untouched.

        :param str affiliate_id: The unique identifier of the affiliate to be updated.
        :param AffiliatePatch input_data: The data to update the affiliate with.
        :return: The updated Affiliate object.
        :rtype: Affiliate
        :raises NotFoundException: If the affiliate is not found.
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}

        if not update_data:
            raise ValueError("No valid fields provided for update.")

        updated_affiliate = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(affiliate_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if updated_affiliate:
            return Affiliate(**updated_affiliate)
        else:
            raise NotFoundException(Affiliate.__name__)

    def delete(self, affiliate_id: str) -> Optional[Affiliate]:
        """
        Delete an affiliate from the database based on its ID.

        This method locates an affiliate in the database using the provided affiliate_id and deletes it.
        If the affiliate is found and deleted, it returns an Affiliate object initialized with the deleted affiliate's details.
        If no affiliate is found, it returns None.

        :param str affiliate_id: The unique identifier of the affiliate to be deleted.
        :return: An instance of Affiliate initialized with the deleted affiliate's details, or None if no affiliate is found.
        :rtype: Affiliate | None
        :raises NotFoundException: If the affiliate is not found.
        """
        affiliate = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(affiliate_id)}
        )

        if affiliate:
            return Affiliate(**affiliate)
        else:
            raise NotFoundException(Affiliate.__name__)

