from bson import ObjectId
from tests import IntegrationTest

import lib.constants as constants


class OperatingSystemsTestCase(IntegrationTest):

    def test_create_operating_system(self):
        # given
        operating_system = self.fixtures.operating_system.clone()
        admin_user = self.fixtures.admin_user

        tokens = self.models.logins.login(admin_user.email, constants.strong_password)

        # when
        response = self.app.post(
            "/v1/admin/operating-systems",
            headers={"Authorization": f'Bearer {tokens["access_token"]}'},
            json=operating_system.to_json()
        )

        actual = response.get_json().get("data")

        self.addCleanup(lambda: self.factory.operating_systems.cleanup(ObjectId(actual.get("_id"))))

        # then
        expected = operating_system.clone()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(expected.name, actual.get("name"))
