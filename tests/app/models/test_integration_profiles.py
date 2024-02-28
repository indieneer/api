from unittest.mock import MagicMock

import firebase_admin.auth
from bson import ObjectId

from app.models.profiles import ProfileCreate, ProfilesModel
from tests.integration_test import IntegrationTest
from tests.mocks.firebase import mock_auth_method


class ProfilesModelTestCase(IntegrationTest):

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
