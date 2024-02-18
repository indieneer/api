from unittest.mock import ANY, MagicMock, patch

import bson.errors
import firebase_admin.auth
import firebase_admin.exceptions
from bson import ObjectId
from flask import session
from pymongo.collection import Collection

from app.models.profiles import Profile, ProfilesModel
from app.services.firebase import Firebase
from config.constants import FirebaseRole
from testicles.unit_test import UnitTest
from tests.mocks.database import mock_collection_method
from tests.mocks.firebase import mock_auth_method

db_mock = MagicMock()
firebase_mock = MagicMock()

mock_id = ObjectId()
mock_profile = Profile(
    _id=mock_id,
    email="john.doe@gmail.com",
    nickname="john_doe",
    display_name="John Doe",
    photo_url="https://images.com/image.png",
    idp_id=str(mock_id),
    roles=[FirebaseRole.User.value]
)


class ProfilesTestCase(UnitTest):

    @patch("app.models.tags.Database")
    def test_get(self, db: MagicMock):

        def finds_a_profile():
            # given
            model = ProfilesModel(db=db, firebase=MagicMock())

            find_one_mock = mock_collection_method(db, ProfilesModel.collection, Collection.find_one.__name__)
            find_one_mock.return_value = mock_profile.to_json()

            # when
            result = model.get(str(mock_profile._id))

            # then
            self.assertEqual(result, mock_profile)
            find_one_mock.assert_called_once_with({"_id": mock_profile._id})

        def does_not_find_a_profile_and_returns_none():
            # given
            mock_id = ObjectId()
            model = ProfilesModel(db=db, firebase=MagicMock())

            find_one_mock = mock_collection_method(db, ProfilesModel.collection, Collection.find_one.__name__)
            find_one_mock.return_value = None

            # when
            result = model.get(str(mock_id))

            # then
            self.assertIsNone(result)
            find_one_mock.assert_called_once_with({"_id": mock_id})

        def raises_an_error_when_id_is_invalid():
            # given
            mock_id = 'invalid'
            model = ProfilesModel(db=db, firebase=MagicMock())

            find_one_mock = mock_collection_method(db, ProfilesModel.collection, Collection.find_one.__name__)

            # when
            with self.assertRaises(bson.errors.InvalidId):
                model.get(mock_id)

            # then
            find_one_mock.assert_not_called()

        tests = [
            finds_a_profile,
            does_not_find_a_profile_and_returns_none,
            raises_an_error_when_id_is_invalid
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db.reset_mock()

    @patch("app.models.tags.Database")
    def test_find_by_email(self, db: MagicMock):

        def finds_a_profile():
            model = ProfilesModel(db=db, firebase=MagicMock())

            find_one_mock = mock_collection_method(db, ProfilesModel.collection, Collection.find_one.__name__)
            find_one_mock.return_value = mock_profile.to_json()

            # when
            result = model.find_by_email(mock_profile.email)

            # then
            self.assertEqual(result, mock_profile)
            find_one_mock.assert_called_once_with({"email": mock_profile.email})

        def does_not_find_a_profile_and_returns_none():
            # given
            mock_email = "john.doe@gmail.com"
            model = ProfilesModel(db=db, firebase=MagicMock())

            find_one_mock = mock_collection_method(db, ProfilesModel.collection, Collection.find_one.__name__)
            find_one_mock.return_value = None

            # when
            result = model.find_by_email(mock_email)

            # then
            self.assertIsNone(result)
            find_one_mock.assert_called_once_with({"email": mock_email})

        tests = [
            finds_a_profile,
            does_not_find_a_profile_and_returns_none
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db.reset_mock()

    @patch("app.models.tags.Database")
    def test_delete_db_profile(self, db: MagicMock):

        def deletes_and_returns_a_profile():
            # given
            model = ProfilesModel(db=db, firebase=MagicMock())

            find_one_and_delete_mock = mock_collection_method(
                db,
                ProfilesModel.collection,
                Collection.find_one_and_delete.__name__
            )
            find_one_and_delete_mock.return_value = mock_profile.to_json()

            # when
            result = model.delete_db_profile(str(mock_profile._id))

            # then
            self.assertEqual(result, mock_profile)
            find_one_and_delete_mock.assert_called_once_with({"_id": mock_profile._id})

        def when_profile_does_not_exist_it_does_not_delete_a_profile():
            model = ProfilesModel(db=db, firebase=MagicMock())

            mock_id = ObjectId()
            find_one_and_delete_mock = mock_collection_method(
                db,
                ProfilesModel.collection,
                Collection.find_one_and_delete.__name__
            )
            find_one_and_delete_mock.return_value = None

            # when
            result = model.delete_db_profile(str(mock_id))

            # then
            self.assertIsNone(result)
            find_one_and_delete_mock.assert_called_once_with({"_id": mock_id})

        tests = [
            deletes_and_returns_a_profile,
            when_profile_does_not_exist_it_does_not_delete_a_profile
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db.reset_mock()

    def test_delete(self):

        def deletes_and_returns_a_profile():
            # given
            model = ProfilesModel(db=db_mock, firebase=firebase_mock)

            find_one_and_delete_mock = mock_collection_method(
                db_mock,
                ProfilesModel.collection,
                Collection.find_one_and_delete.__name__
            )
            find_one_and_delete_mock.return_value = mock_profile.to_json()

            delete_user_mock = mock_auth_method(firebase_mock, firebase_admin.auth.delete_user.__name__)
            delete_user_mock.return_value = None

            # when
            result = model.delete(str(mock_profile._id))

            # then
            self.assertEqual(result, mock_profile)
            find_one_and_delete_mock.assert_called_once_with({"_id": mock_profile._id}, session=ANY)
            delete_user_mock.assert_called_once_with(mock_profile.idp_id)

        def when_db_profile_not_found_does_not_delete_a_profile():
            # given
            model = ProfilesModel(db=db_mock, firebase=firebase_mock)

            find_one_and_delete_mock = mock_collection_method(
                db_mock,
                ProfilesModel.collection,
                Collection.find_one_and_delete.__name__
            )
            find_one_and_delete_mock.return_value = None

            delete_user_mock = mock_auth_method(firebase_mock, firebase_admin.auth.delete_user.__name__)

            # when
            result = model.delete(str(mock_profile._id))

            # then
            self.assertIsNone(result)
            find_one_and_delete_mock.assert_called_once_with({"_id": mock_profile._id}, session=ANY)
            delete_user_mock.assert_not_called()

        def when_idp_profile_not_found_raises_an_error():
            # given
            model = ProfilesModel(db=db_mock, firebase=firebase_mock)

            find_one_and_delete_mock = mock_collection_method(
                db_mock,
                ProfilesModel.collection,
                Collection.find_one_and_delete.__name__
            )
            find_one_and_delete_mock.return_value = mock_profile.to_json()

            delete_user_mock = mock_auth_method(firebase_mock, firebase_admin.auth.delete_user.__name__)
            delete_user_mock.side_effect = firebase_admin.exceptions.NotFoundError(firebase_admin.exceptions.NOT_FOUND)

            # when
            with self.assertRaises(firebase_admin.exceptions.NotFoundError):
                model.delete(str(mock_profile._id))

            # then
            find_one_and_delete_mock.assert_called_once_with({"_id": mock_profile._id}, session=ANY)
            delete_user_mock.assert_called_once_with(mock_profile.idp_id)

        tests = [
            deletes_and_returns_a_profile,
            when_db_profile_not_found_does_not_delete_a_profile,
            when_idp_profile_not_found_raises_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()

            db_mock.reset_mock()
            firebase_mock.reset_mock()
