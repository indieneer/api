import time

from bson import ObjectId

from app.models.profiles import ProfileCreate
from tests import IntegrationTest


class ProfilesTestCase(IntegrationTest):
    @property
    def token(self):
        return self.models.logins.login("test_integration+regular@pork.com",
                                        "9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:")["access_token"]

    def test_get_profile(self):
        # given
        profile, cleanup = self.factory.profiles.create(input=ProfileCreate(
            email="test_integration+regular@pork.com",
            password="test_integration",
        ))
        self.addCleanup(cleanup)

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        response = self.app.get(
            f"/v1/profiles/{str(profile._id)}")
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"], profile.to_json())

    def test_get_profile_not_found(self):
        # when
        time.sleep(0.5)  # Temporary fix for free plan
        response = self.app.get(f"/v1/profiles/{ObjectId()}")

        # then
        self.assertEqual(response.get_json()["error"], "\"Profile\" not found.")
        self.assertEqual(response.status_code, 404)

    def test_create_profile(self):
        # given
        profile_data = ProfileCreate(
            email="test_integration_create@pork.com",
            password="test_integration")

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        response = self.app.post(
            "/v1/profiles/",
            json=profile_data.to_json()
        )

        # then
        time.sleep(0.5)  # Temporary fix for free plan
        self.factory.profiles.cleanup(profile_data.email)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"]["email"], profile_data.email)

    def test_create_profile_with_invalid_body(self):
        # given
        profile_data = {
            "email": "test_email@pork.com"
        }

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        response = self.app.post(
            "/v1/profiles/",
            json=profile_data
        )

        # then
        self.assertEqual(response.get_json()["error"], "Bad Request.")
        self.assertEqual(response.status_code, 400)

    def test_update_profile(self):
        self.skipTest("Profile PATCH is not implemented yet.")

    def test_delete_profile(self):
        # given
        profile, cleanup = self.factory.profiles.create(input=ProfileCreate(
            email="test_user_to_be_deleted@pork.com",
            password="test_pork_john"))
        self.addCleanup(cleanup)
        token = self.models.logins.login("test_user_to_be_deleted@pork.com", "test_pork_john")["access_token"]
        expected_output = {
            "status": "ok",
            "data": {
                "acknowledged": True,
            }
        }

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        response = self.app.delete(
            f"/v1/profiles/{str(profile._id)}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # then
        self.assertEqual(response.get_json(), expected_output)
        self.assertEqual(response.status_code, 200)

    def test_delete_profile_not_found(self):
        # given
        profile, cleanup = self.factory.profiles.create(ProfileCreate(
            email="to_be_deleted@pork.com",
            password="pork_pass"
        ))
        profile_id = str(profile._id)
        token = self.models.logins.login("to_be_deleted@pork.com", "pork_pass")["access_token"]
        cleanup()

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        response = self.app.delete(
            f"/v1/profiles/{profile_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # then
        self.assertEqual(response.get_json()["error"], "\"Profile\" not found.")
        self.assertEqual(response.status_code, 404)

    def test_delete_profile_forbidden_when_profile_owned_by_another_user(self):
        # given
        profile, cleanup = self.factory.profiles.create(input=ProfileCreate(
            email="fake_pork@pork.com",
            password="test_pork_john"))
        self.addCleanup(cleanup)

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        response = self.app.delete(
            f"/v1/profiles/{str(profile._id)}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        # then
        self.assertEqual(response.get_json()["error"], "Forbidden.")
        self.assertEqual(response.status_code, 403)

    def test_get_authenticated_profile(self):
        # given
        profile, cleanup = self.factory.profiles.create(ProfileCreate("test_pork_john@pork.com", "pork_pass"))
        self.addCleanup(cleanup)
        token = self.models.logins.login("test_pork_john@pork.com",
                                         "pork_pass")["access_token"]

        # when
        time.sleep(0.5)  # Temporary fix for free plan
        response = self.app.get(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"], profile.to_json())

    def test_get_authenticated_profile_not_found(self):
        # given
        _, cleanup = self.factory.profiles.create(ProfileCreate(
            email="to_be_deleted@pork.com",
            password="pork_pass"
        ))
        token = self.models.logins.login("to_be_deleted@pork.com", "pork_pass")["access_token"]
        cleanup()

        # when
        time.sleep(0.5)
        response = self.app.get(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "\"Profile\" not found.")
