from dataclasses import dataclass
from typing import List, Optional, cast

import firebase_admin.auth
import pymongo.errors
from bson import ObjectId
from pymongo import ReturnDocument

from app.models.base import BaseDocument, Serializable
from app.services import Database
from app.services.firebase import Firebase
from config import app_config
from config.constants import FirebaseRole


class Profile(BaseDocument):
    email: str
    nickname: str
    display_name: str
    photo_url: str
    idp_id: str
    roles: List[str]

    def __init__(
        self,
        email: str,
        nickname: str,
        display_name: str,
        photo_url: str,
        idp_id: str,
        roles: List[str],
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.email = email
        self.nickname = nickname
        self.display_name = display_name
        self.photo_url = photo_url
        self.idp_id = idp_id
        self.roles = roles


@dataclass
class ProfileCreate(Serializable):
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
    firebase: Firebase
    collection: str = "profiles"

    def __init__(self, db: Database, firebase: Firebase) -> None:
        self.db = db
        self.firebase = firebase

    def get(self, profile_id: str):
        """
        Retrieve a user profile based on the user ID.

        This function searches the database for a profile matching the provided user ID.
        If a profile is found, it is returned as a Profile object.

        :param str user_id: The ID of the user whose profile is being retrieved.
        :return: A Profile object if the user profile is found, otherwise None.
        :rtype: Profile or None
        """
        profile = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(profile_id)})

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
        """Creates a user using Firebase provider

        Args:
            input_data (ProfileCreate): Attributes that will be used to create a user

        Returns:
            Profile: Created profile
        """
        UserRecord = self.firebase.auth.UserRecord

        # Use display name or nickname as the initial display name
        display_name = input_data.display_name or input_data.nickname
        # Use generated avatar if none is provided
        photo_url = input_data.photo_url or f"https://ui-avatars.com/api/?name={display_name}&background=random"

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
        except firebase_admin.auth.EmailAlreadyExistsError as error:
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
        role = input_data.role or FirebaseRole.User
        try:
            # Try create a profile in database
            profile = Profile(
                email=input_data.email,
                nickname=input_data.nickname,
                display_name=user.display_name or display_name,
                photo_url=user.photo_url or photo_url,
                idp_id=cast(str, user.uid),
                roles=[role.value],
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

    def delete(self, profile_id: str):
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
                self.firebase.auth.delete_user(profile.idp_id)

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
        raise Exception("Not implemented")

        update_data = input_data.to_bson()

        profile = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if profile is not None:
            return Profile(**profile)
