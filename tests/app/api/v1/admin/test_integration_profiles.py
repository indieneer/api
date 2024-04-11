from lib.constants import strong_password
from tests import IntegrationTest


class ProfilesTestCase(IntegrationTest):
    def test_get_profiles(self):
        # given
        profile = self.fixtures.admin_user
        tokens = self.factory.logins.login(profile.email, strong_password)

        # when
        response = self.app.get(
            "/v1/admin/profiles", headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        self.assertIsInstance(response.get_json()["data"], list)
        self.assertGreater(len(response.get_json()["data"]), 0)
