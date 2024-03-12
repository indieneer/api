import json
from unittest.mock import patch

from app.api.v1.logins import logins
from app.services.firebase.identity_toolkit import FirebaseUserIdentity
from tests import UnitTest


class LoginsTestCase(UnitTest):

    @patch("app.api.v1.logins.get_models")
    def test_logins(self, mock_get_models):
        # given
        endpoint = "/logins"
        self.app.route(endpoint, methods=["POST"])(logins)

        email = "johnpork@gmail.com"

        mock_login = mock_get_models.return_value.logins.login
        mock_token = FirebaseUserIdentity(identity={
            "idToken": "abcd.efghijkl.mnop",
            "email": email
        })
        mock_login.return_value = mock_token

        data = {"email": email, "password": "password"}

        # when
        response = self.test_client.post(
            endpoint, data=json.dumps(data), content_type="application/json")

        # then
        self.assertEqual(
            response.get_json(),
            {
                'data': mock_token.to_json(),
                'status': 'ok'
            }
        )
        self.assertEqual(response.status_code, 200)
        mock_login.assert_called_with(
            email,
            "password",
        )
