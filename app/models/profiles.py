import dis
from typing import Optional, cast
from bson import ObjectId
from dataclasses import dataclass
from click import Option

import pymongo.errors

from app.services import Database, ManagementAPI
from app.services.firebase import Firebase
from config import app_config
from config.constants import AUTH0_ROLES, Auth0Role, FirebaseRole
from app.models.base import BaseDocument, Serializable


class Profile(BaseDocument):
    email: str
    nickname: str
    display_name: str
    photo_url: str
    idp_id: str

    def __init__(
        self,
        email: str,
        nickname: str,
        display_name: str,
        photo_url: str,
        idp_id: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.email = email
        self.nickname = nickname
        self.display_name = display_name
        self.photo_url = photo_url
        self.idp_id = idp_id


@dataclass
class ProfileCreate(Serializable):
    email: str
    password: str


@dataclass
class ProfileCreateV2(Serializable):
    email: str
    password: str
    nickname: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: Optional[bool] = False
    role: Optional[FirebaseRole] = None


@dataclass
class ProfilePatch(Serializable):
    email: Optional[str] = None
    password: Optional[str] = None


class ProfilesModel:
    db: Database
    auth0: ManagementAPI
    firebase: Firebase
    collection: str = "profiles"

    def __init__(self, db: Database, firebase: Firebase, auth0: ManagementAPI) -> None:
        self.db = db
        self.firebase = firebase
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
        profile = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(user_id)})

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
        profile = self.db.connection[self.collection].find_one(
            {"email": email})

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
        self.auth0.client.users.update(
            idp_id, {"user_metadata": {"profile_id": str(profile._id)}})

        return profile

    def create_v2(self, input_data: ProfileCreateV2):
        """Creates a user using Firebase provider

        Args:
            input_data (ProfileCreateV2): Attributes that will be used to create a user

        Returns:
            Profile: Created profile
        """
        UserRecord = self.firebase.auth.UserRecord

        # Use display name or nickname as the initial display name
        display_name = input_data.display_name or input_data.nickname
        # Use generated avatar if none is provided
        photo_url = input_data.photo_url or f"https://ui-avatars.com/api/?name={input_data.display_name}&background=random"

        # Create the user in Firebase
        user: UserRecord | None = None
        try:
            user = self.firebase.auth.create_user(
                # Use ObjectId as UID so we can relate database and Firebase users
                uid=str(ObjectId()),
                email=input_data.email,
                password=input_data.password,
                display_name=display_name,
                photo_url=photo_url,
                email_verified=input_data.email_verified
            )
            user = cast(UserRecord, user)
        except self.firebase.auth.EmailAlreadyExistsError as error:
            # We expect a user existence in 2 cases:
            # - user creation failed on one of the below steps and we are re-creating it
            # - user creation succeeded
            user = self.firebase.auth.get_user_by_email(input_data.email)
            user = cast(UserRecord, user)

            # If custom claims are set then the user is fully set up,
            # don't let the user continue
            if user.custom_claims is not None and f"{app_config['FB_NAMESPACE']}/profile_id" in user.custom_claims:
                raise error
        except Exception as error:
            raise error

        # Create a user profile in the database
        # Identity provider ID will be the same as Mongo user profile's _id
        profile: Profile | None = None
        try:
            # Try create a profile in database
            profile = Profile(
                email=input_data.email,
                nickname=input_data.nickname,
                display_name=display_name,
                photo_url=photo_url,
                idp_id=cast(str, user.uid),
                _id=ObjectId(user.uid)
            )
            self.db.connection[self.collection].insert_one(profile.to_bson())
        except pymongo.errors.DuplicateKeyError as error:
            # We expect a user existence in 1 case:
            # - set_custom_user_claims failed on the previous sign up attempt
            profile = self.db.connection[self.collection].find_one(
                {"_id": ObjectId(user.uid)})

            if profile is None:
                raise Exception("Profile is None")

            profile = Profile(**profile)
        except Exception as error:
            raise error

        # Set custom claims: roles, profile_id, permissions
        # Important: setting custom claims removes previously defined claims
        role = input_data.role or FirebaseRole.User
        custom_claims = dict([
            (f"{app_config['FB_NAMESPACE']}/profile_id", str(profile._id)),
            (f"{app_config['FB_NAMESPACE']}/roles", [role.value]),
            (f"{app_config['FB_NAMESPACE']}/permissions", []),
        ])
        try:
            self.firebase.auth.set_custom_user_claims(user.uid, custom_claims)
        except Exception as error:
            raise error

        return profile

    def patch_v2(self, input_data: ProfilePatch):
        pass

    def delete_v2(self, profile_id: str):
        # Perform the deletion in transaction to handle failed Firebase operation
        with self.db.client.start_session() as session:
            with session.start_transaction():
                profile = self.db.connection[self.collection].find_one_and_delete(
                    {"_id": ObjectId(profile_id)},
                    session=session
                )
                if profile is None:
                    return

                profile = Profile(**profile)

                # Delete user in Firebase
                self.firebase.auth.delete_user(profile_id)

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
        existing_profile = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(user_id)})
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
        updated_profile = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(user_id)})

        if updated_profile is not None:
            return Profile(**updated_profile)

    def delete(self, user_id: str):
        """
        Delete a user profile.

        This method finds and deletes the user profile based on the provided user ID.
        It also deletes the user from the authentication system (Auth0).

        :param str user_id: The ID of the user whose profile is to be deleted.
        :raises: NotFoundException if the profile is not found.
        :return: The deleted Profile object, if found and deleted successfully.
        :rtype: Profile
        """
        profile = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(user_id)}
        )

        profile = Profile(**profile)
        # Delete the user from Auth0
        self.auth0.client.users.delete(profile.idp_id)

        return profile
