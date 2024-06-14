from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo.errors import OperationFailure

from app.models.base import BaseDocument
from app.services import Database
from lib.db_utils import Serializable


class PopularOnSteam(BaseDocument):
    product_slug: str
    order_index: int

    def __init__(self, product_slug: str, order_index: int, **kwargs):
        super().__init__(**kwargs)

        self.product_slug = product_slug
        self.order_index = order_index


@dataclass
class PopularOnSteamCreate(Serializable):
    product_slug: str
    order_index: int


@dataclass
class PopularOnSteamPatch(Serializable):
    product_slug: Optional[str] = None
    order_index: Optional[int] = None


class PopularOnSteamModel:
    db: Database
    collection: str = "popular_on_steam"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get_all(self) -> List[PopularOnSteam]:
        products = []

        for product in self.db.connection[self.collection].find().sort("order_index", 1):
            products.append(PopularOnSteam(**product))

        return products

    def create(self, input_data: PopularOnSteamCreate) -> PopularOnSteam:
        with self.db.client.start_session() as session:
            with session.start_transaction():
                try:
                    existing_index = self.db.connection[self.collection].find_one(
                        {"order_index": input_data.order_index},
                        session=session)
                    if existing_index:
                        # If the order_index exists, increment all subsequent order_indexes by 1
                        self.db.connection[self.collection].update_many(
                            {"order_index": {"$gte": input_data.order_index}},
                            {"$inc": {"order_index": 1}},
                            session=session
                        )

                    popular_on_steam = PopularOnSteam(**input_data.to_bson())
                    self.db.connection[self.collection].insert_one(popular_on_steam.to_bson(), session=session)
                    return popular_on_steam
                except OperationFailure:
                    session.abort_transaction()
                    raise Exception("Insertion failed, transaction aborted")

    def patch(self, popular_on_steam_id: str, input_data: PopularOnSteamPatch) -> Optional[PopularOnSteam]:
        with self.db.client.start_session() as session:
            with session.start_transaction():
                try:
                    current_data = self.db.connection[self.collection].find_one(
                        {"_id": ObjectId(popular_on_steam_id)}, session=session
                    )
                    if not current_data:
                        return None

                    if input_data.order_index is not None and input_data.order_index != current_data['order_index']:
                        new_index = input_data.order_index
                        old_index = current_data['order_index']

                        if new_index > old_index:
                            self.db.connection[self.collection].update_many(
                                {"order_index": {"$lte": new_index, "$gt": old_index}},
                                {"$inc": {"order_index": -1}},
                                session=session
                            )
                        else:
                            self.db.connection[self.collection].update_many(
                                {"order_index": {"$lt": old_index, "$gte": new_index}},
                                {"$inc": {"order_index": 1}},
                                session=session
                            )

                    updates = {key: value for key, value in input_data.to_json().items() if value is not None}
                    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.db.connection[self.collection].update_one(
                        {"_id": ObjectId(popular_on_steam_id)},
                        {"$set": updates},
                        session=session
                    )

                    updated_popular_on_steam_data = self.db.connection[self.collection].find_one(
                        {"_id": ObjectId(popular_on_steam_id)},
                        session=session
                    )
                    return PopularOnSteam(**updated_popular_on_steam_data) if updated_popular_on_steam_data else None
                except OperationFailure:
                    session.abort_transaction()
                    raise Exception("Update failed, transaction aborted.")

    def delete(self, popular_on_steam_id: str) -> int:
        popular_on_steam = self.db.connection[self.collection].delete_one({"_id": ObjectId(popular_on_steam_id)})

        return popular_on_steam.deleted_count
