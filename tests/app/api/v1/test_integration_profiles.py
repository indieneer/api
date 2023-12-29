from app.middlewares.requires_auth import create_test_token
from app.models.profiles import ProfileCreate
from tests import IntegrationTest


class ProfilesTestCase(IntegrationTest):
    token = create_test_token(profile_id="1", idp_id="1")

    def test_get_profile(self):
        # given
        profile, cleanup = self.factory.profiles.create(input=ProfileCreate(
            email="test_integration+regular@pork.com",
            password="9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:"
        ))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(
            f"/v1/profiles/{str(profile._id)}")
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"], profile.to_json())
