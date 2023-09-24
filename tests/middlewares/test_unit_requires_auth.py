from flask import Flask
import unittest
from unittest.mock import patch, Mock, MagicMock

from app.middlewares import requires_auth, AuthError


class RequiresAuthTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.testing = True

    @patch('app.middlewares.requires_auth.app_config', MagicMock())
    @patch('app.middlewares.requires_auth.get_token_auth_header', Mock(return_value="Bearer test"))
    @patch('app.middlewares.requires_auth.jwt.get_unverified_header')
    @patch('app.middlewares.requires_auth.jwt.decode')
    @patch('app.middlewares.requires_auth.requests.get')
    def test_correct_token(
        self,
        requests_get: MagicMock,
        jwt_decode: MagicMock,
        get_unverified_header: MagicMock
    ):
        # given
        mock_jwks_response = {
            "keys": [
                {
                    "kid": "test1",
                    "kty": "test",
                    "use": "test",
                    "n": "test",
                    "e": "test"
                }
            ]
        }
        mock_unverified_header = {
            "kid": "test1"
        }
        mock_decoded_payload = {
            "sub": "auth0|abcdedfghijklmnop"
        }
        mock_handler = Mock()
        mock_handler.return_value = "Simple handler response"

        requests_get.return_value.json.return_value = mock_jwks_response
        get_unverified_header.return_value = mock_unverified_header
        jwt_decode.return_value = mock_decoded_payload

        # when
        with self.app.test_request_context(
            "/", method="GET"
        ):
            result = requires_auth(mock_handler)()

            # then
            get_unverified_header.assert_called_once_with("Bearer test")
            mock_handler.assert_called_once()
            self.assertEqual(result, "Simple handler response")

    @patch('app.middlewares.requires_auth.requests.get', Mock(return_value=Mock()))
    @patch('app.middlewares.requires_auth.app_config', MagicMock())
    @patch('app.middlewares.requires_auth.get_token_auth_header')
    def test_incorrect_token(self, get_token_auth_header):
        # given
        get_token_auth_header.side_effect = AuthError(
            {"description": "test error", "code": "invalid_header"}, 401)

        # when
        with self.app.test_request_context(
            "/", method="GET"
        ):
            handler = Mock()
            with self.assertRaises(AuthError) as e:
                requires_auth(handler)()

            # then
            self.assertEqual(e.exception.status_code, 401)
            self.assertEqual(e.exception.error["description"], "test error")
            handler.assert_not_called()
