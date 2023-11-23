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

    def test_get_profile(self):
        pass

    def test_update_profile(self):
        pass

    def test_delete_profile(self):
        pass

    def test_get_authenticated_profile(self):
        pass
