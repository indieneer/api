from typing import Optional
from bson import ObjectId
from dataclasses import dataclass

from app.services import Database, ManagementAPI
from config.constants import AUTH0_ROLES, Auth0Role
from app.models.base import BaseDocument, Serializable


class Profile(BaseDocument):
    email: str
    idp_id: str

    def __init__(
        self,
        email: str,
        idp_id: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

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
        """
        Retrieve a user profile based on the user ID.

        This function searches the database for a profile matching the provided user ID.
        If a profile is found, it is returned as a Profile object.

        :param str user_id: The ID of the user whose profile is being retrieved.
        :return: A Profile object if the user profile is found, otherwise None.
        :rtype: Profile or None
        """
        profile = self.db.connection[self.collection].find_one({"_id": ObjectId(user_id)})

        if profile is not None:
            return Profile(**profile)

    def find_by_email(self, email: str):
        """
        Retrieve a user profile based on the user's email.

        This function searches the database for a profile matching the provided email.
        If a profile is found, it is returned as a Profile object.

        :param str email: The email of the user whose profile is being retrieved.
        :return: A Profile object if the user profile is found, otherwise None.
        :rtype: Profile or None
        """
        profile = self.db.connection[self.collection].find_one({"email": email})

        if profile is not None:
            return Profile(**profile)

    def create(self, input_data: ProfileCreate):
        """
        Create a new user profile.

        This function first creates a user in Auth0 with the provided details.
        It assigns roles to the user, creates a user profile in the database,
        and updates the Auth0 user metadata with the internal profile ID.

        :param ProfileCreate input_data: The data required to create a new user profile.
        :return: A Profile object representing the newly created user profile.
        :rtype: Profile
        """
        # Create the user in Auth0
        auth0_user = self.auth0.client.users.create({
            "email": input_data.email,
            "password": input_data.password,
            "email_verified": True,
            "connection": "Username-Password-Authentication"
        })

        idp_id = auth0_user["user_id"]
        roles = [AUTH0_ROLES[Auth0Role.User.value]]

        # Assign a role to the user
        self.auth0.client.users.add_roles(idp_id, roles)

        # Create a user profile in the database
        profile_data = input_data.to_json()
        profile_data['idp_id'] = idp_id
        profile = Profile(**profile_data)
        self.db.connection[self.collection].insert_one(profile.to_bson())

        # Store internal user ID in Auth0 user's metadata
        self.auth0.client.users.update(idp_id, {"user_metadata": {"profile_id": str(profile._id)}})

        return profile

    def patch(self, user_id: str, input_data: ProfilePatch):
        """
        Update an existing user profile with the provided data.

        This function finds a user profile by its unique ID and updates it with the given input data.
        It only updates the fields provided in the input_data, leaving other fields unchanged.

        :param str user_id: The ID of the user whose profile is to be updated.
        :param ProfilePatch input_data: The data to update in the user profile.
        :return: The updated Profile object or None.
        :rtype: Profile or None
        """
        # Find the existing profile
        existing_profile = self.db.connection[self.collection].find_one({"_id": ObjectId(user_id)})
        if not existing_profile:
            return None  # Might be changed to an exception raise

        # Prepare the update data
        update_data = input_data.to_bson()

        # Update the profile in the database
        self.db.connection[self.collection].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        # Fetch the updated profile
        updated_profile = self.db.connection[self.collection].find_one({"_id": ObjectId(user_id)})
        
        if updated_profile is not None:
            return Profile(**updated_profile)

    def delete(self, user_id: str):
        """
        Delete a user profile.

        This method finds and deletes the user profile based on the provided user ID.
        It also deletes the user from the authentication system (Auth0).

        :param str user_id: The ID of the user whose profile is to be deleted.
        :return: The deleted Profile object, if found and deleted successfully.
        :rtype: Profile
        """
        profile = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(user_id)}
        )

        if profile is not None:
            profile = Profile(**profile)
            # Delete the user from Auth0
            self.auth0.client.users.delete(profile.idp_id)

            return profile
