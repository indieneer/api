import json
from unittest.mock import patch, MagicMock

from tests import UnitTest

from app.models.profiles import ProfileCreate, Profile


class ProfilesTestCase(UnitTest):

    @patch("app.api.v1.profiles.get_models")
    def test_create_profile(self, get_models: MagicMock):
        create_profile_mock = get_models.return_value.profiles.create

        def call_api(body):
            return self.app.post(
                "/v1/profiles",
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
                "data": mock_profile.as_json()
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
            expected_response = {
                "status": "error",
                "error": "Exception: BANG!"
            }

            # when
            response = call_api({
                "email": expected_input.email,
                "password": expected_input.password
            })

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 500)
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
        get_profile_mock = get_models.return_value.profiles.get

        def call_api(profileId):
            return self.app.get(
                f"/v1/profiles/{profileId}",
                content_type='application/json'
            )

        def finds_and_returns_a_profile():
            # given
            mock_profile = Profile(
                email="john.pork@test.com", idp_id="auth0|test")
            get_profile_mock.return_value = mock_profile

            expected_response = {
                "status": "ok",
                "data": mock_profile.as_json()
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

    def test_update_profile(self):
        pass

    def test_delete_profile(self):
        pass

    def test_get_authenticated_profile(self):
        pass
