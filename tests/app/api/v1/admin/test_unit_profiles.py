from unittest.mock import patch

from app.middlewares.requires_auth import create_test_token
from app.models.profiles import Profile
from tests import UnitTest


class ProfilesTestCase(UnitTest):
    @patch("app.api.v1.admin.profiles.get_models")
    def test_get_profiles(self, get_models):
        get_all_profiles_mock = get_models.return_value.profiles.get_all

        def call_api():
            return self.app.get(
                f"/v1/admin/profiles/",
                headers={"Authorization": "Bearer " + create_test_token("", roles=["Admin", "User"])}
            )

        def finds_all_profiles():
            # given
            mock_profiles = [
                Profile(
                    email="john1@pork.com",
                    idp_id="auth0|pork1"
                ),
                Profile(
                    email="john2@pork.com",
                    idp_id="auth0|pork2"
                ),
            ]
            get_all_profiles_mock.return_value = mock_profiles
            expected_response = {
                "status": "ok",
                "data": [profile.to_json() for profile in mock_profiles]
            }

            # when
            response = call_api()

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)

        def does_not_find_profiles_and_returns_empty_list():
            # given
            get_all_profiles_mock.return_value = []
            expected_response = {
                "status": "ok",
                "data": []
            }

            # when
            response = call_api()

            # then
            self.assertEqual(response.get_json(), expected_response)
            self.assertEqual(response.status_code, 200)

        tests = [
            finds_all_profiles,
            does_not_find_profiles_and_returns_empty_list
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            get_all_profiles_mock.reset_mock()

    @patch("app.api.v1.admin.profiles.get_models")
    def test_change_profile(self, get_models):
        self.skipTest("PATCH is not implemented yet.")
