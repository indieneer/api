from typing import cast
from unittest.mock import MagicMock, patch

from bson import ObjectId

from app.models.logins import LoginsModel
from app.models.profiles import Profile
from app.services.firebase.exceptions import InvalidLoginCredentialsException
from app.services.firebase.identity_toolkit.dto import FirebaseUserIdentity
from config.constants import FirebaseRole
from tests import UnitTest
from tests.mocks.app_config import mock_app_config
from tests.utils.comparators import ANY_NUMBER

# Reuse mock
db_mock = MagicMock()
firebase_mock = MagicMock()
profiles_model = MagicMock()
service_profiles_model = MagicMock()
logins_model = LoginsModel(firebase=firebase_mock, profiles=profiles_model, service_profiles=service_profiles_model)


class LoginsTestCase(UnitTest):

    @patch("app.models.profiles.app_config")
    def test_login(self, app_config: MagicMock):
        sign_in_mock = cast(MagicMock, firebase_mock.identity_api.sign_in)
        verify_id_token_mock = cast(MagicMock, firebase_mock.auth.verify_id_token)
        get_profile_mock = cast(MagicMock, profiles_model.get)
        app_config_mock = mock_app_config(app_config, {
            "FB_NAMESPACE": "https://indieneer.com"
        })

        def after_test():
            self.reset_mock(db_mock)
            self.reset_mock(sign_in_mock)

        def logins():
            # given
            profile_id = ObjectId()
            email = "john.doe@gmail.com"
            password = "john.doe@2"
            mock_identity = FirebaseUserIdentity(idToken="abcd.efghijklmnop.qrstuv")
            claims = dict([(f"{app_config_mock['FB_NAMESPACE']}/profile_id", str(profile_id))])

            sign_in_mock.return_value = mock_identity
            verify_id_token_mock.return_value = claims
            get_profile_mock.return_value = Profile(
                display_name="John",
                email=email,
                idp_id=str(profile_id),
                nickname="john",
                photo_url="https://images.com/image.png",
                roles=[FirebaseRole.User.value]
            )

            # when
            result = logins_model.login(email, password)

            # then
            sign_in_mock.assert_called_once_with(email, password)
            verify_id_token_mock.assert_called_once_with(mock_identity.id_token, clock_skew_seconds=ANY_NUMBER())
            get_profile_mock.assert_called_once_with(str(profile_id))
            self.assertEqual(result, mock_identity)

        def fails_to_login_with_wrong_credentials():
            # given
            email = "john.doe@gmail.com"
            password = "john.doe@2"
            sign_in_mock.side_effect = InvalidLoginCredentialsException()

            # when
            with self.assertRaises(InvalidLoginCredentialsException):
                logins_model.login(email, password)

            # then
            sign_in_mock.assert_called_once_with(email, password)

        tests = [
            logins,
            fails_to_login_with_wrong_credentials,
        ]

        self.run_subtests(tests, after_each=after_test)

    def test_login_m2m(self):
        self.skipTest("Implement later.")

    def test_exchange_refresh_token(self):
        self.skipTest("Implement later.")
