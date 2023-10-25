import json
from unittest.mock import patch
from tests import UnitTest


class LoginsTestCase(UnitTest):

    @patch("app.api.v1.logins.get_models")
    def test_logins(self, mock_get_models):
        # given
        mock_login = mock_get_models.return_value.logins.login

        mock_token = {"access_token": "token123"}

        mock_login.return_value = mock_token

        data = {"email": "johnpork@gmail.com", "password": "password"}

        # when
        response = self.app.post("/v1/logins", data=json.dumps(data), content_type="application/json")

        # then
        self.assertEqual(response.get_json(), {'data': mock_token, 'status': 'ok'})
        self.assertEqual(response.status_code, 200)
        mock_login.assert_called_with(
            "johnpork@gmail.com",
            "password",
        )
