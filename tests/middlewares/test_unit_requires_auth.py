from flask import Flask, g
from unittest.mock import patch, Mock, MagicMock

from app.middlewares import requires_auth, AuthError
from tests.unit_test import UnitTest
from tests.utils.jwt import MockRequiresAuthExtension


class RequiresAuthTestCase(UnitTest):

    def setUp(self) -> None:
        self.app = Flask(__name__)
        auth_extension = MockRequiresAuthExtension()
        auth_extension.init_app(self.app)

    @patch('app.middlewares.requires_auth.get_token_auth_header', Mock(return_value="Bearer test"))
    @patch('app.middlewares.requires_auth.get_requires_auth')
    def test_correct_token(self, get_requires_auth: MagicMock):
        # given
        mock_decoded_payload = {
            "sub": "auth0|abcdedfghijklmnop"
        }
        mock_handler = Mock()
        mock_handler.return_value = "Simple handler response"
        
        verify_token_mock = get_requires_auth.return_value.verify_token
        verify_token_mock.return_value = mock_decoded_payload

        # when
        with self.app.test_request_context(
            "/", method="GET"
        ):
            result = requires_auth(mock_handler)()

            # then
            verify_token_mock.assert_called_once_with("Bearer test")
            self.assertEqual(g.payload, mock_decoded_payload)
            mock_handler.assert_called_once()
            self.assertEqual(result, "Simple handler response")

    @patch('app.middlewares.requires_auth.get_token_auth_header', Mock(return_value="Bearer invalid"))
    @patch('app.middlewares.requires_auth.get_requires_auth')
    def test_incorrect_token(self, get_requires_auth: MagicMock):
        # given
        get_requires_auth.return_value.verify_token.side_effect = AuthError(
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
