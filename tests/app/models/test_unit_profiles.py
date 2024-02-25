import json
from unittest.mock import ANY, MagicMock, patch

import bson.errors
import firebase_admin.auth
import firebase_admin.exceptions
from bson import ObjectId
from pymongo.collection import Collection

from app.models.profiles import Profile, ProfileCreate, ProfilesModel
from app.services.firebase import Firebase
from config import app_config
from config.constants import FirebaseRole
from lib.db_utils import to_json
from testicles.unit_test import UnitTest
from tests.mocks.app_config import mock_app_config
from tests.mocks.database import mock_collection_method
from tests.mocks.firebase import mock_auth_method
from tests.utils.jwt import TEST_AUTH_NAMESPACE

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

    def test_get(self):
        model = ProfilesModel(db=db_mock, firebase=firebase_mock)

        def finds_a_profile():
            # given
            find_one_mock = mock_collection_method(db_mock, ProfilesModel.collection, Collection.find_one.__name__)
            find_one_mock.return_value = mock_profile.to_json()

            # when
            result = model.get(str(mock_profile._id))

            # then
            self.assertEqual(result, mock_profile)
            find_one_mock.assert_called_once_with({"_id": mock_profile._id})

        def does_not_find_a_profile_and_returns_none():
            # given
            mock_id = ObjectId()

            find_one_mock = mock_collection_method(db_mock, ProfilesModel.collection, Collection.find_one.__name__)
            find_one_mock.return_value = None

            # when
            result = model.get(str(mock_id))

            # then
            self.assertIsNone(result)
            find_one_mock.assert_called_once_with({"_id": mock_id})

        def raises_an_error_when_id_is_invalid():
            # given
            mock_id = 'invalid'

            find_one_mock = mock_collection_method(db_mock, ProfilesModel.collection, Collection.find_one.__name__)

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
            db_mock.reset_mock()

    def test_find_by_email(self):
        model = ProfilesModel(db=db_mock, firebase=firebase_mock)

        def finds_a_profile():
            # given
            find_one_mock = mock_collection_method(db_mock, ProfilesModel.collection, Collection.find_one.__name__)
            find_one_mock.return_value = mock_profile.to_json()

            # when
            result = model.find_by_email(mock_profile.email)

            # then
            self.assertEqual(result, mock_profile)
            find_one_mock.assert_called_once_with({"email": mock_profile.email})

        def does_not_find_a_profile_and_returns_none():
            # given
            mock_email = "john.doe@gmail.com"

            find_one_mock = mock_collection_method(db_mock, ProfilesModel.collection, Collection.find_one.__name__)
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
            db_mock.reset_mock()

    def test_delete_db_profile(self):
        model = ProfilesModel(db=db_mock, firebase=firebase_mock)

        def deletes_and_returns_a_profile():
            # given
            find_one_and_delete_mock = mock_collection_method(
                db_mock,
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
            # given
            mock_id = ObjectId()
            find_one_and_delete_mock = mock_collection_method(
                db_mock,
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
            db_mock.reset_mock()

    def test_delete(self):
        model = ProfilesModel(db=db_mock, firebase=firebase_mock)

        def deletes_and_returns_a_profile():
            # given
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

    @patch("app.models.profiles.app_config")
    def test_create(self, app_config_mock: MagicMock):
        UserRecord = firebase_admin.auth.UserRecord
        model = ProfilesModel(db=db_mock, firebase=firebase_mock)
        app_config_mock = mock_app_config(app_config_mock, {
            "FB_NAMESPACE": TEST_AUTH_NAMESPACE
        })

        def creates_a_profile():
            create_user_mock = mock_auth_method(firebase_mock, firebase_admin.auth.create_user.__name__)
            insert_one_mock = mock_collection_method(
                db_mock, ProfilesModel.collection, Collection.insert_one.__name__)
            set_custom_user_claims_mock = mock_auth_method(
                firebase_mock, firebase_admin.auth.set_custom_user_claims.__name__)

            tests = [
                {
                    "name": "with_default_configuration",
                    "input_data": ProfileCreate(
                        email="john.doe@gmail.com",
                        password="john_doe_123456",
                        nickname="john_doe",
                    ),
                    "asserts": lambda input_data: {
                        "display_name": input_data.nickname,
                        "photo_url": f"https://ui-avatars.com/api/?name={input_data.nickname}&background=random",
                        "email_verified": False,
                        "role": FirebaseRole.User.value,
                    }
                },
                {
                    "name": "with_custom_display_name",
                    "input_data": ProfileCreate(
                        email="john.doe@gmail.com",
                        password="john_doe_123456",
                        nickname="john_doe",
                        display_name="John Doe"
                    ),
                    "asserts": lambda input_data: {
                        "display_name": input_data.display_name,
                        "photo_url": f"https://ui-avatars.com/api/?name={input_data.display_name}&background=random",
                        "email_verified": False,
                        "role": FirebaseRole.User.value,
                    }
                },
                {
                    "name": "with_custom_photo_url",
                    "input_data": ProfileCreate(
                        email="john.doe@gmail.com",
                        password="john_doe_123456",
                        nickname="john_doe",
                        photo_url="https://example.com/image.png"
                    ),
                    "asserts": lambda input_data: {
                        "display_name": input_data.nickname,
                        "photo_url": input_data.photo_url,
                        "email_verified": False,
                        "role": FirebaseRole.User.value,
                    }
                },
                {
                    "name": "with_custom_role",
                    "input_data": ProfileCreate(
                        email="john.doe@gmail.com",
                        password="john_doe_123456",
                        nickname="john_doe",
                        role=FirebaseRole.Admin,
                    ),
                    "asserts": lambda input_data: {
                        "display_name": input_data.nickname,
                        "photo_url": f"https://ui-avatars.com/api/?name={input_data.nickname}&background=random",
                        "email_verified": False,
                        "role": FirebaseRole.Admin.value,
                    }
                },
                {
                    "name": "with_email_verified",
                    "input_data": ProfileCreate(
                        email="john.doe@gmail.com",
                        password="john_doe_123456",
                        nickname="john_doe",
                        email_verified=True
                    ),
                    "asserts": lambda input_data: {
                        "display_name": input_data.nickname,
                        "photo_url": f"https://ui-avatars.com/api/?name={input_data.nickname}&background=random",
                        "email_verified": True,
                        "role": FirebaseRole.User.value,
                    }
                },
                {
                    "name": "with_all_custom_values",
                    "input_data": ProfileCreate(
                        email="john.doe@gmail.com",
                        password="john_doe_123456",
                        nickname="john_doe",
                        email_verified=True,
                        display_name="John Doe",
                        photo_url="https://example.com/image.png",
                        role=FirebaseRole.Admin
                    ),
                    "asserts": lambda input_data: {
                        "display_name": input_data.display_name,
                        "photo_url": input_data.photo_url,
                        "email_verified": True,
                        "role": FirebaseRole.Admin.value,
                    }
                },
            ]

            for test in tests:
                with self.subTest(test["name"]):
                    # given
                    input_data = test["input_data"]

                    # - mock firebase user
                    def create_user_side_effect(user_id_mock: dict):
                        def side_effect(**kwargs):
                            user_id_mock["value"] = kwargs["uid"]

                            return UserRecord({
                                "localId": kwargs["uid"],
                                "displayName": kwargs["display_name"],
                                "email": kwargs["email"],
                                "photoUrl": kwargs["photo_url"],
                                "emailVerified": kwargs["email_verified"]
                            })

                        return side_effect
                    user_id_mock: dict = {"value": None}
                    create_user_mock.side_effect = create_user_side_effect(user_id_mock)

                    # - mock db user
                    def create_insert_one_side_effect(profile_mock: dict):
                        def side_effect(bson_object: dict):
                            profile_mock["value"] = Profile(**bson_object)

                        return side_effect
                    profile_mock: dict[str, Profile | None] = {"value": None}
                    insert_one_mock.side_effect = create_insert_one_side_effect(profile_mock)

                    # when
                    result = model.create(input_data)

                    # then
                    asserts = test["asserts"](input_data)

                    create_user_mock.assert_called_once_with(
                        uid=user_id_mock["value"],
                        email=input_data.email,
                        password=input_data.password,
                        display_name=asserts["display_name"],
                        photo_url=asserts["photo_url"],
                        email_verified=asserts["email_verified"])
                    insert_one_mock.assert_called_once_with(profile_mock["value"].to_bson())
                    set_custom_user_claims_mock.assert_called_once_with(user_id_mock["value"], dict([
                        (f"{app_config['FB_NAMESPACE']}/profile_id", str(profile_mock["value"]._id)),
                        (f"{app_config['FB_NAMESPACE']}/roles", [asserts["role"]]),
                        (f"{app_config['FB_NAMESPACE']}/permissions", []),
                    ]))
                    self.assertEqual(result.to_json(), profile_mock["value"].to_json())

                create_user_mock.reset_mock()
                insert_one_mock.reset_mock()
                set_custom_user_claims_mock.reset_mock()

        def when_fails_to_create_a_firebase_user():
            input_data = ProfileCreate(
                email="john.doe@gmail.com",
                password="john_doe_123456",
                nickname="john_doe",
            )
            create_user_mock = mock_auth_method(firebase_mock, firebase_admin.auth.create_user.__name__)

            def when_exception():
                # given
                create_user_mock.side_effect = Exception('BANG!')

                # when
                with self.assertRaises(Exception) as context:
                    model.create(input_data)

                # then
                self.assertEqual(context.exception, create_user_mock.side_effect)

            def when_user_already_exists():
                get_user_by_email_mock = mock_auth_method(firebase_mock, firebase_admin.auth.get_user_by_email.__name__)

                def when_custom_claims_are_set_raises_an_error():
                    # given
                    mock_id = str(ObjectId())
                    customAttributes = {}
                    customAttributes[f"{app_config['FB_NAMESPACE']}/profile_id"] = mock_id
                    get_user_by_email_mock.return_value = UserRecord({
                        "localId": mock_id,
                        "customAttributes": json.dumps(customAttributes)
                    })

                    # when
                    with self.assertRaises(firebase_admin.auth.EmailAlreadyExistsError) as context:
                        model.create(input_data)

                    # then
                    self.assertEqual(context.exception, create_user_mock.side_effect)

                def when_custom_claims_are_not_set_creates_a_user():
                    return
                    # given
                    mock_id = ObjectId()
                    get_user_by_email_mock.return_value = UserRecord({
                        "localId": str(mock_id),
                        # if a user exists, we use his display name instead of a new one
                        "displayName": "Existing Name",
                        "email": input_data.email,
                        "photoUrl": input_data.photo_url,
                        "emailVerified": input_data.email_verified
                    })

                    insert_one_mock = mock_collection_method(
                        db_mock, ProfilesModel.collection, Collection.insert_one.__name__)

                    # when
                    result = model.create(input_data)

                    # then
                    expected_result = Profile()

                    self.assertEqual(result.to_json(), expected_result.to_json())

                tests = [
                    when_custom_claims_are_set_raises_an_error,
                    when_custom_claims_are_not_set_creates_a_user
                ]

                for test in tests:
                    # reuse mocks
                    create_user_mock.side_effect = firebase_admin.auth.EmailAlreadyExistsError(
                        "already exists", "", 409)

                    with self.subTest(test.__name__):
                        test()

                    create_user_mock.reset_mock()

            tests = [
                when_exception,
                when_user_already_exists
            ]

            for test in tests:
                with self.subTest(test.__name__):
                    test()
                create_user_mock.reset_mock()

        tests = [
            creates_a_profile,
            when_fails_to_create_a_firebase_user
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            db_mock.reset_mock()
            firebase_mock.reset_mock()
