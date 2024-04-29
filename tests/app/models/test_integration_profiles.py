from datetime import datetime
from typing import cast
from unittest.mock import MagicMock

import firebase_admin.auth
import pymongo.errors
from bson import ObjectId

from app.models.profiles import ProfileCreate, ProfilesModel
from config import app_config
from config.constants import FirebaseRole
from tests.integration_test import IntegrationTest
from tests.mocks.firebase import mock_auth_method
from tests.utils.comparators import ANY_DATE, ANY_OBJECTID, ANY_STR


class ProfilesModelTestCase(IntegrationTest):
    def test_get_all(self):
        model = ProfilesModel(db=self.services.db, firebase=self.services.firebase)

        def finds_all_profiles():
            # when
            result = model.get_all()

            # then
            self.assertIsNotNone(result)
            self.assertGreater(len(result), 0)

        tests = [
            finds_all_profiles,
        ]

        self.run_subtests(tests)

    def test_get(self):
        model = ProfilesModel(db=self.services.db, firebase=self.services.firebase)

        def finds_a_profile():
            # given
            fixture = self.fixtures.regular_user

            # when
            result = model.get(str(fixture._id))

            # then
            self.assertIsNotNone(result)
            self.assertEqual(result._id, fixture._id)

        def does_not_find_a_profile():
            # given
            mock_id = ObjectId()

            # when
            result = model.get(str(mock_id))

            # then
            self.assertIsNone(result)

        tests = [
            finds_a_profile,
            does_not_find_a_profile,
        ]

        self.run_subtests(tests)

    def test_find_by_email(self):
        model = ProfilesModel(db=self.services.db, firebase=self.services.firebase)

        def finds_a_profile():
            # given
            fixture = self.fixtures.regular_user

            # when
            result = model.get(str(fixture._id))

            # then
            self.assertIsNotNone(result)
            self.assertEqual(result._id, fixture._id)
            self.assertEqual(result.email, fixture.email)

        def does_not_find_a_profile():
            # given
            mock_email = "john.doe@nonexisting.com"

            # when
            result = model.find_by_email(mock_email)

            # then
            self.assertIsNone(result)

        tests = [
            finds_a_profile,
            does_not_find_a_profile,
        ]

        self.run_subtests(tests)

    def test_delete(self):
        model = ProfilesModel(db=self.services.db, firebase=self.services.firebase)

        profile, cleanup = self.factory.profiles.create(ProfileCreate(
            display_name="John Doe",
            email="john.doe@gmail.com",
            nickname="john_doe",
            password="John_Doe@235"
        ))
        self.addCleanup(cleanup)

        def deletes_a_profile_and_returns_it():
            # when
            result = model.delete(str(profile._id))

            # then
            self.assertIsNotNone(result)
            self.assertEqual(result._id, profile._id)

            with self.assertRaises(firebase_admin.auth.UserNotFoundError):
                self.services.firebase.auth.get_user(result.idp_id)

        def when_db_profile_does_not_exist_returns_none():
            # when
            result = model.delete(str(profile._id))

            # then
            self.assertIsNone(result)

        # mocking firebase error to test the db transaction
        def when_fails_to_delete_firebase_profile_reverts_db_profile():
            # given
            firebase_mock = MagicMock()
            model = ProfilesModel(db=self.services.db, firebase=firebase_mock)

            delete_user_mock = mock_auth_method(firebase_mock, firebase_admin.auth.delete_user.__name__)
            delete_user_mock.side_effect = firebase_admin.auth.InsufficientPermissionError("", "", 403)

            profile, cleanup = self.factory.profiles.create(ProfileCreate(
                display_name="John Doe",
                email="john.doe@gmail.com",
                nickname="john_doe",
                password="John_Doe@235"
            ))
            self.addCleanup(cleanup)

            # when
            with self.assertRaises(firebase_admin.auth.InsufficientPermissionError):
                model.delete(str(profile._id))

            # then
            delete_user_mock.assert_called_once_with(profile.idp_id)

            reverted_profile = self.models.profiles.get(str(profile._id))
            self.assertIsNotNone(reverted_profile)

        tests = [
            deletes_a_profile_and_returns_it,
            when_db_profile_does_not_exist_returns_none,
            when_fails_to_delete_firebase_profile_reverts_db_profile
        ]

        self.run_subtests(tests)

    def test_patch(self):
        self.skipTest("Not implemented")

    def test_create(self):
        model = ProfilesModel(db=self.services.db, firebase=self.services.firebase)

        def creates_a_profile():
            # given
            input_data = ProfileCreate(
                display_name="John Doe",
                email="create_profile_integration@gmail.com",
                nickname="create_profile",
                password="John@235",
            )

            # when
            profile = model.create(input_data)
            self.addCleanup(lambda: self.factory.profiles.cleanup(profile.email))

            # then
            expected_result = {
                "_id": ANY_OBJECTID(),
                "display_name": input_data.display_name,
                "nickname": input_data.nickname,
                "email": input_data.email,
                "photo_url": f"https://ui-avatars.com/api/?name={input_data.display_name}&background=random",
                "roles": [FirebaseRole.User.value],
                "idp_id": ANY_STR(),
                "created_at": ANY_DATE(before=datetime.now()),
                "updated_at": ANY_DATE(before=datetime.now()),
            }
            self.assertDictEqual(expected_result, profile.to_bson())

            fb_profile = cast(firebase_admin.auth.UserRecord, self.services.firebase.auth.get_user(profile.idp_id))
            self.assertEqual(profile.email, fb_profile.email)
            self.assertEqual(dict([
                (f"{app_config['FB_NAMESPACE']}/profile_id", str(profile._id)),
                (f"{app_config['FB_NAMESPACE']}/roles", [FirebaseRole.User.value]),
                (f"{app_config['FB_NAMESPACE']}/permissions", []),
            ]), fb_profile.custom_claims)

        def creates_an_admin_profile():
            # given
            input_data = ProfileCreate(
                display_name="John Doe Admin",
                email="create_admin_profile_integration@gmail.com",
                nickname="john_doe_admin",
                password="John@235",
                role=FirebaseRole.Admin
            )

            # when
            profile = model.create(input_data)
            self.addCleanup(lambda: self.factory.profiles.cleanup(profile.email))

            # then
            expected_result = {
                "_id": ANY_OBJECTID(),
                "display_name": input_data.display_name,
                "nickname": input_data.nickname,
                "email": input_data.email,
                "photo_url": f"https://ui-avatars.com/api/?name={input_data.display_name}&background=random",
                "roles": [FirebaseRole.Admin.value],
                "idp_id": ANY_STR(),
                "created_at": ANY_DATE(before=datetime.now()),
                "updated_at": ANY_DATE(before=datetime.now()),
            }
            self.assertDictEqual(expected_result, profile.to_bson())

            fb_profile = cast(firebase_admin.auth.UserRecord, self.services.firebase.auth.get_user(profile.idp_id))
            self.assertEqual(profile.email, fb_profile.email)
            self.assertEqual(dict([
                (f"{app_config['FB_NAMESPACE']}/profile_id", str(profile._id)),
                (f"{app_config['FB_NAMESPACE']}/roles", [FirebaseRole.Admin.value]),
                (f"{app_config['FB_NAMESPACE']}/permissions", []),
            ]), fb_profile.custom_claims)

        def fails_to_create_a_profile_with_existing_email():
            # given
            input_data = ProfileCreate(
                display_name="John Doe Admin",
                email=self.fixtures.regular_user.email,
                nickname="john_doe_admin",
                password="John@235",
                role=FirebaseRole.Admin
            )

            # when
            with self.assertRaises(firebase_admin.auth.EmailAlreadyExistsError):
                model.create(input_data)

        def fails_to_create_a_profile_with_existing_nickname():
            # given
            input_data = ProfileCreate(
                display_name="John Doe",
                email="create_profile_integration_nick@gmail.com",
                nickname=self.fixtures.regular_user.nickname,
                password="John@235",
            )
            self.addCleanup(lambda: self.factory.profiles.cleanup(input_data.email))

            # when
            with self.assertRaises(pymongo.errors.DuplicateKeyError):
                model.create(input_data)

        tests = [
            creates_a_profile,
            creates_an_admin_profile,
            fails_to_create_a_profile_with_existing_email,
            # TODO: fails_to_create_a_profile_with_existing_nickname
        ]

        self.run_subtests(tests)
