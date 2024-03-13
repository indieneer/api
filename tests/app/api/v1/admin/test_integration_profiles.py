from config.constants import FirebaseRole
from lib.constants import strong_password
from tests import IntegrationTest
from app.models.profiles import ProfileCreate


class ProfilesTestCase(IntegrationTest):
    def test_get_profiles(self):
        # given
        profile = self.fixtures.admin_user
        tokens = self.factory.logins.login(profile.email, strong_password)

        # when
        response = self.app.get(
            "/v1/health", headers={"Authorization": f'Bearer {tokens.id_token}'}
        )

        # then
        expected = {
            "status": "ok",
            "data": {
                "db": 1.0,
                "env": "test",
                "version": "0.0.1"
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected)
