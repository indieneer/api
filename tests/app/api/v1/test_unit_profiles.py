import json
from unittest.mock import patch, MagicMock

from tests import UnitTest

from app.models.profiles import ProfileCreate, Profile


class ProfilesTestCase(UnitTest):

    def test_get_profiles(self):
        # TODO: rework
        self.assertEqual(1, 1)

    @patch("app.api.v1.profiles.get_models")
    def test_create_profile(self, get_models: MagicMock):
        # given
        mock_profile = Profile(email="john.pork@test.com", idp_id="auth0|test")

        create_profile_mock = get_models.return_value.profiles.create
        create_profile_mock.return_value = mock_profile

        # when
        response = self.app.post(
            "/v1/profiles",
            data=json.dumps({
                "email": mock_profile.email,
                "password": "123456789"
            }),
            content_type='application/json'
        )

        # then
        expected_response = {
            "status": "ok",
            "data": mock_profile.as_json()
        }
        expected_input = ProfileCreate(
            email=mock_profile.email,
            password="123456789"
        )

        self.assertEqual(response.get_json(), expected_response)
        self.assertEqual(response.status_code, 201)
        create_profile_mock.assert_called_once_with(expected_input)
