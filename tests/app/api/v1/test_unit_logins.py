import json
from unittest.mock import patch, Mock
from tests import UnitTest


class LoginsTestCase(UnitTest):

    @patch("app.api.v1.logins.GetToken")
    @patch("app.api.v1.logins.app_config")
    def test_logins(self, mock_app_config, mock_get_token):
        # given
        mock_app_config.__getitem__.side_effect = lambda key: {
            "AUTH0_DOMAIN": "pork.com",
            "AUTH0_CLIENT_ID": "client_id",
            "AUTH0_CLIENT_SECRET": "client_secret",
            "AUTH0_AUDIENCE": "audience"
        }[key]

        mock_login = mock_get_token.return_value.login

        mock_token = {"access_token": "token123"}

        mock_login.return_value = mock_token

        data = {"email": "johnpork@gmail.com", "password": "password"}

        # when
        response = self.app.post("/v1/logins", data=json.dumps(data), content_type="application/json")

        # then
        self.assertEqual(response.get_json(), {'data': mock_token, 'status': 'ok'})
        self.assertEqual(response.status_code, 200)
        mock_login.assert_called_with(
            username="johnpork@gmail.com",
            password="password",
            realm='Username-Password-Authentication',
            scope="openid profile email address phone offline_access",
            grant_type="password",
            audience="audience"
        )