import jwt

from app.models.logins import LoginsModel
from app.services.firebase.exceptions import InvalidLoginCredentialsException
from config import app_config
from config.constants import FirebaseRole
from lib import constants
from tests.integration_test import IntegrationTest


class LoginsModelTestCase(IntegrationTest):

    def test_login(self):
        # given
        logins_model = LoginsModel(
            firebase=self.services.firebase,
            profiles=self.models.profiles,
            service_profiles=self.models.service_profiles
        )

        def logins_as_a_regular_user():
            # when
            result = logins_model.login(self.fixtures.regular_user.email, constants.strong_password)

            access_token = result.id_token
            # TODO: replace with firebase token validator
            decoded = jwt.decode(access_token, options={"verify_signature": False})

            # then
            self.assertEqual(
                decoded[f'{app_config["FB_NAMESPACE"]}/profile_id'],
                str(self.fixtures.regular_user._id)
            )
            self.assertIn(
                FirebaseRole.User.value,
                decoded[f'{app_config["FB_NAMESPACE"]}/roles']
            )

        def logins_as_an_admin_user():
            # when
            result = logins_model.login(self.fixtures.admin_user.email, constants.strong_password)

            access_token = result.id_token
            # TODO: replace with firebase token validator
            decoded = jwt.decode(access_token, options={"verify_signature": False})

            # then
            self.assertEqual(
                decoded[f'{app_config["FB_NAMESPACE"]}/profile_id'],
                str(self.fixtures.admin_user._id)
            )
            self.assertIn(
                FirebaseRole.Admin.value,
                decoded[f'{app_config["FB_NAMESPACE"]}/roles']
            )

        def fails_to_login_with_not_existing_email():
            # when
            with self.assertRaises(InvalidLoginCredentialsException):
                logins_model.login("abcdefghi@not.existing", constants.strong_password)

        def fails_to_login_with_wrong_password():
            # when
            with self.assertRaises(InvalidLoginCredentialsException):
                logins_model.login(self.fixtures.admin_user.email, constants.weak_password)

        tests = [
            logins_as_a_regular_user,
            logins_as_an_admin_user,
            fails_to_login_with_not_existing_email,
            fails_to_login_with_wrong_password,
        ]

        self.run_subtests(tests)
