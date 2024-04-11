from unittest.mock import patch, MagicMock
import json

from bson import ObjectId

from app.api.v1.profiles import create_profile, get_profile, update_profile, delete_profile, get_authenticated_profile
from app.models.exceptions import NotFoundException, ForbiddenException
from config.constants import FirebaseRole

from tests import UnitTest
from app.models.profiles import ProfileCreate, Profile, ProfilePatch
from tests.mocks.app_config import mock_app_config
from tests.utils.jwt import create_test_token, TEST_AUTH_NAMESPACE


class ProfilesTestCase(UnitTest):
    @patch("app.api.v1.profiles.get_models")
    def test_create_profile(self, get_models: MagicMock):
        endpoint = "/profiles"
        self.app.route(endpoint, methods=["POST"])(create_profile)

        create_profile_mock = get_models.return_value.profiles.create

        def call_api(body):
            return self.test_client.post(
                endpoint,
                data=json.dumps(body),
                content_type='application/json'
            )

        def creates_and_returns_a_profile():
            # given
            mock_id = ObjectId()
            mock_profile = Profile(
                _id=mock_id, idp_id=str(mock_id), email="john.pork@test.com", nickname="johnny",
                display_name="John Pork",
                photo_url="http://porkphoto.com", roles=[FirebaseRole.User.value])
            create_profile_mock.return_value = mock_profile

            expected_input = ProfileCreate(
                email=mock_profile.email,
                password="123456789",
                nickname=mock_profile.nickname
            )

            expected_response = {
                "status": "ok",
                "data": mock_profile.to_json()
            }

            # when
            response = call_api({
                "email": expected_input.email,
                "password": expected_input.password,
                "nickname": expected_input.nickname
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_profile_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_profile_and_returns_an_error():
            # given
            create_profile_mock.side_effect = Exception("BANG!")

            expected_input = ProfileCreate(
                email="john.pork@test.com",
                password="123456789",
                nickname="johnny"
            )

            # when
            with self.assertRaises(Exception) as context:
                call_api({
                    "email": expected_input.email,
                    "password": expected_input.password,
                    "nickname": expected_input.nickname
                })

            # then
            self.assertEqual(str(context.exception), str(
                create_profile_mock.side_effect))
            create_profile_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_profile_when_body_is_invalid():
            # given
            expected_response = {
                "status": "error",
                "error": "Bad Request."
            }

            # when
            response = call_api({
                "email": "test@mail.com",
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 400)
            create_profile_mock.assert_not_called()

        tests = [
            creates_and_returns_a_profile,
            fails_to_create_a_profile_and_returns_an_error,
            fails_to_create_a_profile_when_body_is_invalid
        ]

        def after_each():
            create_profile_mock.reset_mock()

        self.run_subtests(tests, after_each=after_each)

    @patch("app.api.v1.profiles.get_models")
    def test_get_profile(self, get_models: MagicMock):
        endpoint = "/profiles/<string:profile_id>"
        self.app.route(endpoint)(get_profile)

        get_profile_mock = get_models.return_value.profiles.get

        def call_api(profile_id):
            return self.test_client.get(
                endpoint.replace("<string:profile_id>", profile_id),
                content_type='application/json'
            )

        def finds_and_returns_a_profile():
            # given
            mock_id = ObjectId()
            mock_profile = Profile(
                _id=mock_id, idp_id=str(mock_id), email="john.pork@test.com", nickname="johnny",
                display_name="John Pork",
                photo_url="http://porkphoto.com", roles=[FirebaseRole.User.value])
            get_profile_mock.return_value = mock_profile
            mock_profile_id_str = str(mock_profile._id)

            expected_response = {
                "status": "ok",
                "data": mock_profile.to_json()
            }

            # when
            response = call_api(mock_profile_id_str)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_profile_mock.assert_called_once_with(mock_profile_id_str)

        def does_not_find_a_profile_and_returns_an_error():
            # given
            mock_id = "1"
            get_profile_mock.return_value = None

            # when
            with self.assertRaises(NotFoundException):
                call_api(mock_id)

            # then
            get_profile_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_profile,
            does_not_find_a_profile_and_returns_an_error
        ]

        def after_each():
            get_profile_mock.reset_mock()

        self.run_subtests(tests, after_each=after_each)

    @patch("app.api.v1.profiles.get_models")
    def test_patch_profile(self, get_models: MagicMock):
        self.skipTest("Fix when patch handler & model implemented")
        endpoint = "/profiles/<string:profile_id>"
        self.app.route(endpoint, methods=["PATCH"])(update_profile)

        patch_profile_mock = get_models.return_value.profiles.patch

        def call_api(profile_id, body):
            token = create_test_token(profile_id)

            return self.test_client.patch(
                endpoint.replace("<string:profile_id>", profile_id),
                data=json.dumps(body),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def patches_and_returns_the_profile():
            # given
            mock_id = ObjectId()
            mock_profile = Profile(
                _id=mock_id, idp_id=str(mock_id), email="john.pork@test.com", nickname="johnny",
                display_name="John Pork", photo_url="http://porkphoto.com", roles=[FirebaseRole.User.value])
            patch_profile_mock.return_value = mock_profile

            mock_profile_id_str = str(mock_profile._id)

            expected_input = ProfilePatch(
                email=mock_profile.email,
            )
            expected_response = {
                "status": "ok",
                "data": mock_profile.to_json()
            }

            response = call_api(mock_profile_id_str, {
                "email": expected_input.email,
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            patch_profile_mock.assert_called_once_with(
                mock_profile_id_str, expected_input)

        tests = [
            patches_and_returns_the_profile
        ]

        def after_each():
            patch_profile_mock.reset_mock()

        self.run_subtests(tests, after_each=after_each)

    @patch("app.api.v1.profiles.app_config")
    @patch("app.api.v1.profiles.get_models")
    def test_delete_profile(self, get_models: MagicMock, app_config_mock: MagicMock):
        endpoint = "/profiles/<string:profile_id>"
        self.app.route(endpoint)(delete_profile)

        delete_profile_mock = get_models.return_value.profiles.delete
        mock_app_config(app_config_mock, {
            "FB_NAMESPACE": TEST_AUTH_NAMESPACE
        })

        def call_api(profile_id, token=None):
            if token is None:
                token = create_test_token(profile_id)

            return self.test_client.get(
                endpoint.replace("<string:profile_id>", profile_id),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def deletes_and_returns_the_profile():
            # given
            mock_id = ObjectId()
            mock_profile = Profile(
                _id=mock_id, idp_id=str(mock_id), email="john.pork@test.com", nickname="johnny",
                display_name="John Pork",
                photo_url="http://porkphoto.com", roles=[FirebaseRole.User.value])
            delete_profile_mock.return_value = mock_profile

            mock_profile_id_str = str(mock_profile._id)
            expected_response = {
                "status": "ok",
                "data": {"acknowledged": True}
            }

            # when
            response = call_api(mock_profile_id_str)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            delete_profile_mock.assert_called_once_with(mock_profile_id_str)

        def does_not_find_a_profile_and_returns_an_error():
            # given
            mock_id = "1"
            delete_profile_mock.return_value = None
            delete_profile_mock.side_effect = NotFoundException(Profile.__name__)

            # when
            with self.assertRaises(NotFoundException) as context:
                call_api(mock_id)

            # then
            delete_profile_mock.assert_called_once_with(mock_id)
            self.assertEqual(str(context.exception), str(
                delete_profile_mock.side_effect))

        def fails_to_delete_a_profile_when_invoker_id_does_not_match():
            # given
            false_token = create_test_token("firebase_wrong_id|test")

            # when
            with self.assertRaises(ForbiddenException) as context:
                call_api("1", false_token)

            # then
            self.assertEqual(str(context.exception), str(ForbiddenException()))

        tests = [
            deletes_and_returns_the_profile,
            does_not_find_a_profile_and_returns_an_error,
            fails_to_delete_a_profile_when_invoker_id_does_not_match
        ]

        def after_each():
            delete_profile_mock.reset_mock()

        self.run_subtests(tests, after_each=after_each)

    @patch("app.api.v1.profiles.app_config")
    @patch("app.api.v1.profiles.get_models")
    def test_get_authenticated_profile(self, get_models: MagicMock, app_config_mock: MagicMock):
        endpoint = "/profiles/me"
        self.app.route(endpoint)(get_authenticated_profile)

        get_profile_mock = get_models.return_value.profiles.get
        mock_app_config(app_config_mock, {
            "FB_NAMESPACE": TEST_AUTH_NAMESPACE
        })

        def call_api(profile_id, token=None):
            if token is None:
                token = create_test_token(profile_id)

            return self.test_client.get(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def finds_and_returns_a_profile():
            # given
            mock_id = ObjectId()
            mock_profile = Profile(
                _id=mock_id, idp_id=str(mock_id), email="john.pork@test.com", nickname="johnny",
                display_name="John Pork",
                photo_url="http://porkphoto.com", roles=[FirebaseRole.User.value])
            get_profile_mock.return_value = mock_profile
            mock_profile_id_str = str(mock_profile._id)

            expected_response = {
                "status": "ok",
                "data": mock_profile.to_json()
            }

            # when
            response = call_api(mock_profile_id_str)

            # then
            get_profile_mock.assert_called_once_with(mock_profile_id_str)
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)

        def fails_to_find_a_profile_and_returns_an_error():
            # given
            mock_id = "1"
            get_profile_mock.return_value = None
            get_profile_mock.side_effect = NotFoundException(Profile.__name__)

            # when
            with self.assertRaises(NotFoundException) as context:
                call_api(mock_id)

            # then
            get_profile_mock.assert_called_once_with(mock_id)
            self.assertEqual(str(context.exception), str(
                get_profile_mock.side_effect))

        tests = [
            finds_and_returns_a_profile,
            fails_to_find_a_profile_and_returns_an_error
        ]

        def after_each():
            get_profile_mock.reset_mock()

        self.run_subtests(tests, after_each=after_each)
