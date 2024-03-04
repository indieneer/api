import jwt
from config.constants import FirebaseRole

from lib import constants

from app.models.logins import LoginsModel
from tests.integration_test import IntegrationTest


class LoginsModelTestCase(IntegrationTest):

    def test_login_user(self):
        # given
        logins_model = LoginsModel(
            firebase=self.services.firebase,
            profiles=self.models.profiles,
            service_profiles=self.models.service_profiles
        )

        # when
        result = logins_model.login(
            self.fixtures.regular_user.email, constants.strong_password)

        access_token = result.id_token
        # TODO: replace with firebase token validator
        decoded = jwt.decode(access_token, options={"verify_signature": False})

        # then
        self.assertEqual(
            decoded['https://indieneer.com/profile_id'],
            str(self.fixtures.regular_user._id)
        )
        self.assertNotIn(
            FirebaseRole.Admin.value,
            decoded['https://indieneer.com/roles']
        )
        self.assertIn(
            FirebaseRole.User.value,
            decoded['https://indieneer.com/roles']
        )

    def test_login_admin(self):
        # given
        logins_model = LoginsModel(
            firebase=self.services.firebase,
            profiles=self.models.profiles,
            service_profiles=self.models.service_profiles
        )

        # when
        result = logins_model.login(
            self.fixtures.admin_user.email, constants.strong_password)

        access_token = result.id_token
        # TODO: replace with firebase token validator
        decoded = jwt.decode(access_token, options={"verify_signature": False})

        # then
        self.assertEqual(
            decoded['https://indieneer.com/profile_id'],
            str(self.fixtures.admin_user._id)
        )
        self.assertNotIn(
            FirebaseRole.User.value,
            decoded['https://indieneer.com/roles']
        )
        self.assertIn(
            FirebaseRole.Admin.value,
            decoded['https://indieneer.com/roles']
        )
