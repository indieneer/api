from tests import IntegrationTest
from app.models.profiles import ProfileCreate


class ProfilesTestCase(IntegrationTest):

    def test_get_profiles(self):
        # given
        profile, cleanup_profile = self.factory.profiles.create_admin(
            input=ProfileCreate(
                email=f"{self._testMethodName}@indieneer.com",
                password="Test@234"
            )
        )
        self.addCleanup(cleanup_profile)

        tokens = self.factory.logins.login(profile.email, "Test@234")

        # when
        response = self.app.get(
            "/v1/health", headers={"Authorization": f'Bearer {tokens["access_token"]}'})

        # then
        expected = {
            "status": "ok",
            "data": {
                "db": {"ok": 1},
                "env": "test",
                "version": "0.0.1"
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected)
