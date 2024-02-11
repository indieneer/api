import base64
from dataclasses import dataclass
from enum import Enum
import hmac
from typing import List
from hashlib import sha256
from bson import ObjectId

from app.models.base import BaseDocument
from app.services.database import Database
from app.services.firebase import Firebase
from config import app_config
from lib.db_utils import Serializable


class ServiceProfile(BaseDocument):
    idp_id: str
    client_id: str
    client_secret: str
    permissions: List[str]

    def __init__(
        self,
        idp_id: str,
        client_id: str,
        client_secret: str,
        permissions: List[str],
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.idp_id = idp_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.permissions = permissions


@dataclass
class ServiceProfileCreate(Serializable):
    permissions: List[str]


@dataclass
class ServiceProfilePatch(Serializable):
    permissions: List[str]


class ServiceProfilesModel:
    db: Database
    firebase: Firebase
    collection: str = "service_profiles"

    def __init__(self, db: Database, firebase: Firebase) -> None:
        self.db = db
        self.firebase = firebase

    def get_by_client_id(self, client_id: str):
        profile = self.db.connection[self.collection].find_one({
            "client_id": client_id
        })

        if profile is None:
            return

        return ServiceProfile(**profile)

    def create(self, input_data: ServiceProfileCreate):
        client_id = ObjectId()
        client_secret = hmac.new(
            base64.b32encode(app_config['FB_M2M_SECRET_KEY'].encode("utf-8")),
            str(client_id).encode("utf-8"),
            sha256
        ).hexdigest()

        profile = ServiceProfile(
            idp_id=f"service|{client_id}",
            client_id=str(client_id),
            client_secret=client_secret,
            permissions=input_data.permissions,
            _id=client_id
        )

        self.db.connection[self.collection].insert_one(profile.to_bson())

        return profile

    def patch(self, profile_id: str, input_data: ServiceProfilePatch):
        profile = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(profile_id)},
            {"permissions": input_data.permissions}
        )

        if profile is None:
            return

        return ServiceProfile(**profile)

    def delete_db_profile(self, profile_id: str):
        profile = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(profile_id)},
        )
        if profile is None:
            return

        return ServiceProfile(**profile)

    def delete(self, profile_id: str):
        with self.db.client.start_session() as session:
            with session.start_transaction():
                profile = self.db.connection[self.collection].find_one_and_delete(
                    {"_id": ObjectId(profile_id)},
                    session=session
                )
                if profile is None:
                    return

                profile = ServiceProfile(**profile)

                self.firebase.auth.delete_user(profile.idp_id)

                return profile
