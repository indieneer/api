from datetime import datetime
from unittest.mock import MagicMock

from bson import ObjectId

from app.models import ProfilesModel
from app.models.profiles import ProfileCreate
from tests import UnitTest


class ProfilesModelTestCase(UnitTest):
    mock_db = MagicMock()
    mock_auth0 = MagicMock()
    model = ProfilesModel(mock_db, mock_auth0)
    mock_collection = mock_db.connection.__getitem__.return_value

    def get_new_mock_profile(self):
        return {
            "_id": ObjectId(),
            "email": "mock@pork.com",
            "idp_id": "auth0|mock_pork",
            "created_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "updated_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        }

    def test_get_profile(self):
        def finds_and_return_profile():
            # given
            mock_profile = self.get_new_mock_profile()
            self.mock_collection.find_one.return_value = mock_profile

            # when
            profile = self.model.get(str(mock_profile["_id"]))

            # then
            self.assertEqual(profile.to_dict(), mock_profile)
            self.mock_collection.find_one.assert_called_once_with({"_id": mock_profile["_id"]})

        def does_not_find_profile_and_returns_none():
            # given
            self.mock_collection.find_one.return_value = None

            # when
            profile = self.model.get(str(ObjectId()))

            # then
            self.assertIsNone(profile)
            self.mock_collection.find_one.assert_called_once()

        tests = [
            finds_and_return_profile,
            does_not_find_profile_and_returns_none
        ]

        for test in tests:
            with self.subTest():
                test()
            self.mock_collection.find_one.reset_mock()

    def test_find_by_email(self):
        def finds_and_return_profile():
            # given
            mock_profile = self.get_new_mock_profile()
            self.mock_collection.find_one.return_value = mock_profile

            # when
            profile = self.model.find_by_email(mock_profile["email"])

            # then
            self.assertEqual(profile.to_dict(), mock_profile)
            self.mock_collection.find_one.assert_called_once_with({"email": mock_profile["email"]})

        def does_not_find_profile_and_returns_none():
            # given
            self.mock_collection.find_one.return_value = None

            # when
            profile = self.model.find_by_email("non_existing_email@pork.com")

            # then
            self.assertIsNone(profile)
            self.mock_collection.find_one.assert_called_once()

        tests = [
            finds_and_return_profile,
            does_not_find_profile_and_returns_none
        ]

        for test in tests:
            with self.subTest():
                test()
            self.mock_collection.find_one.reset_mock()

    def test_create_profile(self):
        def creates_and_returns_profile():
            # given
            mock_profile = self.get_new_mock_profile()

            self.mock_collection.insert_one.return_value = mock_profile
            mock_profile_create = ProfileCreate(
                email=mock_profile["email"],
                password="test_pork_password"
            )

            self.mock_auth0.client.users.create.return_value = {
                "user_id": "auth0|mock_pork"
            }

            # when
            profile = self.model.create(mock_profile_create)

            # then
            self.assertEqual(profile.email, mock_profile["email"])
            self.assertEqual(profile.idp_id, mock_profile["idp_id"])
            self.mock_auth0.client.users.create.assert_called_once_with({
                "email": mock_profile["email"],
                "password": mock_profile_create.password,
                "email_verified": True,
                "connection": "Username-Password-Authentication",
            })
            self.mock_collection.insert_one.assert_called_once()

        tests = [
            creates_and_returns_profile
        ]

        for test in tests:
            with self.subTest():
                test()
            self.mock_collection.insert_one.reset_mock()
            self.mock_auth0.client.users.create.reset_mock()

    def test_patch_profile(self):
        self.skipTest("Patch profile is not implemented yet")

    def test_delete_profile(self):
        def deletes_and_returns_profile():
            # given
            mock_profile = self.get_new_mock_profile()
            self.mock_collection.find_one_and_delete.return_value = mock_profile

            # when
            profile = self.model.delete(str(mock_profile["_id"]))

            # then
            self.assertEqual(profile.to_dict(), mock_profile)
            self.mock_collection.find_one_and_delete.assert_called_once_with({"_id": mock_profile["_id"]})
            self.mock_auth0.client.users.delete.assert_called_once_with(mock_profile["idp_id"])

        def does_not_fund_profile_and_returns_none():
            # given
            mock_id = ObjectId()
            self.mock_collection.find_one_and_delete.return_value = None

            # when
            profile = self.model.delete(str(mock_id))

            # then
            self.assertIsNone(profile)
            self.mock_collection.find_one_and_delete.assert_called_once_with({"_id": mock_id})
            self.mock_auth0.client.users.assert_not_called()

        tests = [
            deletes_and_returns_profile,
            does_not_fund_profile_and_returns_none
        ]

        for test in tests:
            with self.subTest():
                test()
            self.mock_collection.find_one_and_delete.reset_mock()
            self.mock_auth0.client.users.delete.reset_mock()
