from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from bson import ObjectId

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

        for product in self.db.connection[self.collection].find():
            products.append(PopularOnSteam(**product))

        return products

    def create(self, input_data: PopularOnSteamCreate) -> PopularOnSteam:
        popular_on_steam = PopularOnSteam(**input_data.to_bson())

        self.db.connection[self.collection].insert_one(popular_on_steam.to_bson())

        return popular_on_steam

    def patch(self, popular_on_steam_id: str, input_data: PopularOnSteamPatch) -> Optional[PopularOnSteam]:
        updates = {key: value for key, value in input_data.to_json().items() if value is not None}
        updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.connection[self.collection].update_one(
            {"_id": ObjectId(popular_on_steam_id)},
            {"$set": updates}
        )

        updated_popular_on_steam_data = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(popular_on_steam_id)}
        )
        if updated_popular_on_steam_data:
            return PopularOnSteam(**updated_popular_on_steam_data)

        return None

    def delete(self, popular_on_steam_id: str) -> int:
        popular_on_steam = self.db.connection[self.collection].delete_one({"_id": ObjectId(popular_on_steam_id)})

        return popular_on_steam.deleted_count
