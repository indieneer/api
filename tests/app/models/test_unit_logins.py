from typing import cast
from unittest.mock import ANY, MagicMock, patch

import pymongo.errors
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.collection import Collection

from app.models.logins import LoginsModel
from app.models.profiles import Profile, ProfilesModel
from app.models.service_profiles import ServiceProfilesModel
from app.services.firebase.identity_toolkit.dto import FirebaseUserIdentity
from config.constants import FirebaseRole
from tests import UnitTest
from tests.mocks.app_config import mock_app_config
from tests.mocks.database import mock_collection_method
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
            # reset mocks here
            self.reset_mock(db_mock)

        def logins():
            # given
            profile_id = ObjectId()
            email = "john.doe@gmail.com"
            password = "john.doe@2"
            mock_identity = FirebaseUserIdentity(idToken="abcdefghijklmnop")
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
            # TODO: add test
            pass

        tests = [
            logins,
            fails_to_login_with_wrong_credentials,
        ]

        self.run_subtests(tests, after_each=after_test)
