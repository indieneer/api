from unittest.mock import patch, MagicMock
import json
from app.api.v1.profiles import create_profile, get_profile, update_profile
from app.models.exceptions import NotFoundException

from bson import ObjectId

from tests import UnitTest
from app.models.profiles import ProfileCreate, Profile, ProfilePatch
from tests.utils.jwt import create_test_token


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
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test")
            create_profile_mock.return_value = mock_profile

            expected_input = ProfileCreate(
                email=mock_profile.email,
                password="123456789"
            )
            expected_response = {
                "status": "ok",
                "data": mock_profile.to_json()
            }

            # when
            response = call_api({
                "email": expected_input.email,
                "password": expected_input.password
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 201)
            create_profile_mock.assert_called_once_with(expected_input)

        def fails_to_create_a_profile_and_returns_an_error():
            # given
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test")
            create_profile_mock.side_effect = Exception("BANG!")

            expected_input = ProfileCreate(
                email=mock_profile.email,
                password="123456789"
            )

            # when
            with self.assertRaises(Exception) as context:
                call_api({
                    "email": expected_input.email,
                    "password": expected_input.password
                })

            # then
            self.assertEqual(str(context.exception), str(create_profile_mock.side_effect))
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

        for test in tests:
            with self.subTest(test.__name__):
                test()
            create_profile_mock.reset_mock()

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
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test")
            get_profile_mock.return_value = mock_profile

            expected_response = {
                "status": "ok",
                "data": mock_profile.to_json()
            }

            # when
            response = call_api(mock_profile._id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_profile_mock.assert_called_once_with(mock_profile._id)

        def does_not_find_a_profile_and_returns_an_error():
            # given
            mock_id = "1"
            get_profile_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": "\"Profile\" not found."
            }

            # when
            with self.assertRaises(NotFoundException):
                response = call_api(mock_id)

                # then
                self.assertEqual(response.get_json(), expected_response)
                self.assertEqual(response.status_code, 404)
                get_profile_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_profile,
            does_not_find_a_profile_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            get_profile_mock.reset_mock()

    @patch("app.api.v1.profiles.get_models")
    def test_patch_profile(self, get_models: MagicMock):
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
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test")
            patch_profile_mock.return_value = mock_profile

            expected_input = ProfilePatch(
                email=mock_profile.email,
            )
            expected_response = {
                "status": "ok",
                "data": mock_profile.to_json()
            }

            response = call_api(mock_profile._id, {
                "email": expected_input.email,
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            patch_profile_mock.assert_called_once_with(
                str(mock_profile._id), expected_input)

        tests = [
            patches_and_returns_the_profile
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            patch_profile_mock.reset_mock()

    @patch("app.api.v1.profiles.get_models")
    def test_delete_profile(self, get_models: MagicMock):
        delete_profile_mock = get_models.return_value.profiles.delete

        def call_api(profile_id):
            token = create_test_token(profile_id)

            return self.app.delete(
                f"/v1/profiles/{profile_id}",
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def deletes_and_returns_the_profile():
            # given
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test"
            )
            mock_id = str(mock_profile._id)
            delete_profile_mock.return_value = mock_profile

            expected_response = {
                "status": "ok",
                "data": {"acknowledged": True}
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            delete_profile_mock.assert_called_once_with(mock_id)

        def fails_to_delete_not_found_profile_and_returns_an_error():
            # given
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test"
            )
            mock_id = str(mock_profile._id)

            delete_profile_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": "\"Profile\" not found."
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            delete_profile_mock.assert_called_once_with(mock_id)

        def fails_to_delete_profile_which_is_owned_by_another_user_and_returns_error():
            # given
            expected_response = {
                "status": "error",
                "error": "Forbidden."
            }

            # when
            token = create_test_token(str(ObjectId()))
            response = self.app.delete(
                "/v1/profiles/1",
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 403)
            delete_profile_mock.assert_not_called()

        tests = [
            deletes_and_returns_the_profile,
            fails_to_delete_not_found_profile_and_returns_an_error,
            fails_to_delete_profile_which_is_owned_by_another_user_and_returns_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                delete_profile_mock.reset_mock()

    @patch("app.api.v1.profiles.get_models")
    def test_get_authenticated_profile(self, get_models: MagicMock):
        get_profile_mock = get_models.return_value.profiles.get

        def call_api(profile_id):
            token = create_test_token(profile_id)

            return self.app.get(
                "/v1/profiles/me",
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json'
            )

        def finds_and_returns_a_profile():
            # given
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test"
            )
            mock_id = str(mock_profile._id)
            get_profile_mock.return_value = mock_profile

            expected_response = {
                "status": "ok",
                "data": mock_profile.to_json()
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)
            get_profile_mock.assert_called_once_with(mock_id)

        def fails_due_to_missing_token_and_returns_an_error():
            # given
            expected_response = {
                "status": "error",
                "error": {
                    "code": "authorization_header_missing",
                    "description": "Authorization header is expected"
                }
            }

            # when
            response = self.app.get(
                "/v1/profiles/me",
                content_type='application/json'
            )

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 401)
            get_profile_mock.assert_not_called()

        def fails_to_find_a_profile_and_returns_an_error():
            # given
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test"
            )
            mock_id = str(mock_profile._id)
            get_profile_mock.return_value = None

            expected_response = {
                "status": "error",
                "error": "\"Profile\" not found."
            }

            # when
            response = call_api(mock_id)

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 404)
            get_profile_mock.assert_called_once_with(mock_id)

        tests = [
            finds_and_returns_a_profile,
            fails_due_to_missing_token_and_returns_an_error,
            fails_to_find_a_profile_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
                get_profile_mock.reset_mock()
