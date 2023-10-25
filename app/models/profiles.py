from typing import Optional
from bson import ObjectId
from dataclasses import dataclass

from app.services import Database, ManagementAPI
from config.constants import AUTH0_ROLES, Auth0Role
from . import BaseDocument, Serializable


class Profile(BaseDocument):
    email: str
    idp_id: str

    def __init__(
        self,
        email: str,
        idp_id: str,
        _id: Optional[ObjectId] = None,
        **kwargs
    ) -> None:
        super().__init__(_id)

        self.email = email
        self.idp_id = idp_id


@dataclass
class ProfileCreate(Serializable):
    email: str
    password: str


@dataclass
class ProfilePatch(Serializable):
    email: Optional[str] = None
    password: Optional[str] = None


class ProfilesModel:
    db: Database
    auth0: ManagementAPI
    collection: str = "profiles"

    def __init__(self, db: Database, auth0: ManagementAPI) -> None:
        self.db = db
        self.auth0 = auth0

    def get(self, user_id: str):
        profile = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(user_id)}
        )

        if profile is not None:
            return Profile(**profile)

    def create(self, input_data: ProfileCreate):
        # Create the user in Auth0
        auth0_user = self.auth0.client.users.create({
            "email": input_data.email,
            "password": input_data.password,
            "email_verified": True,
            "connection": "Username-Password-Authentication"
        })

        idp_id = auth0_user["user_id"]
        roles = [AUTH0_ROLES[Auth0Role.User.value]]

        # Assign a role to user
        self.auth0.client.users.add_roles(idp_id, roles)

        # Create a user in database
        profile = Profile(**input_data.to_json(), idp_id=idp_id).to_json()
        self.db.connection[self.collection].insert_one(profile)

        # Store internal user id on Auth0 user's metadata
        self.auth0.client.users.update(
            idp_id,
            {
                "user_metadata": {
                    "profile_id": str(profile["_id"])
                }
            }
        )

        return Profile(**profile)

    def patch(self, user_id: str, input_data: ProfilePatch):
        raise Exception("Not implemented.")

    def delete(self, user_id: str):
        profile = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(user_id)}
        )

        if profile is not None:
            profile = Profile(**profile)
            self.auth0.client.users.delete(profile.idp_id)
            return profile
